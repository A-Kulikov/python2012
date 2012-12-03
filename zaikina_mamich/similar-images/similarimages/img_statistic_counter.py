__author__ = 'Katerina'

import Image
import colorsys
import math

import logging

logger = logging.getLogger('img_statistic_counter')
logger.setLevel(logging.DEBUG)

class ColorValueTransform:
  def __init__(self):
    raise Exception("Unexpected initialization of class RGBValueTransform.")

  @staticmethod
  def rgb_to_hex_string(rgb):
    hex_chars = "0123456789ABCDEF"
    result = ""
    for i in rgb:
      result += hex_chars[int(i) / 16] + hex_chars[int(i) % 16]
    return "#" + result

  @staticmethod
  def hsv_to_hex_string(hsv):
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    print rgb
    return ColorValueTransform.rgb_to_hex_string(rgb)

  @staticmethod
  def rgb_to_number(rgb):
    result = 0
    for i in rgb:
      result += (result * 256) + i
    return result

  @staticmethod
  def hsv_to_number(hsv):
    #return hsv[0] * 100 + hsv[1] * 50 + hsv[2]
    return int(hsv[0] * 100 * 100 * 100 + hsv[1] * 100 + hsv[2])

  @staticmethod
  def number_to_hsv(num):
    h = num / 10000
    s = (num - h) / 100
    v = num - h - s
    return h, s, v


class ImgStatisticCounter:
  image = None

  histogram = []
  main_colors = []
  expectation_value = 0
  dispersion = 0
  standard_deviation = 0

  __colour_num_ = 256 #ColorValueTransform.rgb_to_number((255, 255, 255)) + 1
  __min_color_difference = ((pow(255, 3) * 3) ** (1 / 3.0)) * 0.01

  def __init__(self, image=None, path=""):
    if image is not None:
      self.image = image
    elif len(path) > 0:
      self.image = Image.open(path)
      self.path = path

    #self.histogram = ImgStatisticCounter.__count_colors_(ImgStatisticCounter.__get_hsv_(self.image))
    self.histogram = ImgStatisticCounter.__count_colors_(self.image.getdata())
    #self.histogram = [(ColorValueTransform.hsv_to_number(x), y) for (x, y) in self.histogram]
    self.histogram.sort(key=lambda (x, y): x)

    self.expectation_value = ImgStatisticCounter.__expectation_value_(self.histogram)
    self.dispersion = ImgStatisticCounter.__dispersion_(self.histogram, self.expectation_value)
    self.standard_deviation = (
      math.sqrt(self.dispersion[0]), math.sqrt(self.dispersion[1]), math.sqrt(self.dispersion[2]))

    self.main_colors = ImgStatisticCounter.__get_main_colors(self.image, self.standard_deviation)

  @staticmethod
  def __get_main_colors(image, deviation):
    image.thumbnail(ImgStatisticCounter.__get_small_size_(image.size, deviation), Image.ANTIALIAS)
    #data = ImgStatisticCounter.__get_hsv_(image)
    data = image.getdata()
    small_hist = ImgStatisticCounter.__count_colors_(data)
    #small_hist.sort(key=lambda (x, y): y)
    #small_hist = small_hist[:min(len(small_hist), 15)]
    result = []
    result_len = 0
    main_colors_count = 5
    for item in small_hist:
      same_idx = -1
      for i in xrange(result_len):
        if not ImgStatisticCounter.__color_is_enough_far(item[0], result[i][0]):
          same_idx = i
          break
      if same_idx == -1:
        result.append(item)
        result_len += 1
      else:
        result[i] = (result[i][0], item[1] + result[i][1])
        #if result_len == main_colors_count:
        #   break


    #for i in xrange(result_len, main_colors_count):
    #    result.append(result[0])
    result.sort(key=lambda (x, y): y)

    return [x for (x, y) in result[:min(5, len(result))]]

  @staticmethod
  def __color_is_enough_far(rgb1, rgb2):
    return ImgStatisticCounter.color_distance(rgb1, rgb2) > ImgStatisticCounter.__min_color_difference

  @staticmethod
  def color_distance(rgb1, rgb2):
    result = 0
    for i in xrange(3):
      result += pow(int(math.fabs(rgb1[i] - rgb2[i])), 3)
    return result ** (1 / 3.0)

  @staticmethod
  def __get_hsv_(image):
    data = image.getdata()
    return [colorsys.rgb_to_hsv(r, g, b) for (r, g, b) in data]

  @staticmethod
  def __get_small_size_(size, deviation):
    #coefficient = max(int(deviation) / 10000, 8);
    return min(size[0], 10), min(size[1], 10)

  @staticmethod
  def __count_colors_(img_data):
    #array = [ColorValueTransform.hsv_to_number(color) for color in img_data]
    color_dict = {}
    for pixel in img_data:
      if not color_dict.has_key(pixel):
        color_dict[pixel] = 0
      color_dict[pixel] += 1
      #return sorted(color_dict.items())
    lst = list(color_dict.items())
    return lst

  @staticmethod
  def __expectation_value_(histogram):
    #s = sum([(r * y, g * y, b * y) for ((r, g, b), y) in histogram])
    result = (0, 0, 0)
    s = 0
    for item in histogram:
      result = (result[0] + (item[0][0] * item[1]),
                result[1] + (item[0][1] * item[1]),
                result[2] + (item[0][2] * item[1]))
      s += item[1]
      #return result
    return (result[0] / (s + 0.0),
            result[1] / (s + 0.0),
            result[2] / (s + 0.0))

  @staticmethod
  def __expected_value_item_count_(item, result, idx):
    return result[idx] + (item[0][idx] * item[1])

  @staticmethod
  def __dispersion_(histogram, expectation_value):
    def channel_dispersion(idx):
      s = sum(pow(expectation_value[idx] - (x[idx] * y), 2) for (x, y) in histogram)
      return s / sum([y for (x, y) in histogram])

    return channel_dispersion(0), channel_dispersion(1), channel_dispersion(2)

  #        s = sum([pow(expectation_value - (x * y), 2) for (x, y) in histogram])
  #        s += pow(expectation_value, 2) * (ImgStatisticCounter.__colour_num_ - len(histogram))
  #        return s / (ImgStatisticCounter.__colour_num_ + 0.0)


  @classmethod
  def distance_between_two_images(cls, ref, image):
    logger.info('distance_between_two_images() entered')
    logger.debug('Reference: {0}'.format(ref))
    logger.debug('Image: {0}'.format(image))

    result = 0
    l = len(image['main_colors'])
    for i in ref['main_colors']:
      arr = [cls.color_distance(i, j) for j in image['main_colors']]
      result += min(arr)

    expectation_values_distance = cls.color_distance(ref['expectation_value'], image['expectation_value'])
    return (l / 2) * expectation_values_distance + result


  def distance(self, ref_statistic):
  #        return [ImgStatisticCounter.__distance_(ref_statistic)]
    result = 0
    l = len(ref_statistic.main_colors)
    for i in self.main_colors:
      arr = [ImgStatisticCounter.color_distance(i, j) for j in ref_statistic.main_colors]
      result += min(arr)
      #result += sum(arr) / l / 2.0

    expected_values_distance = ImgStatisticCounter.color_distance(self.expectation_value,
                                                                  ref_statistic.expectation_value)
    return (l / 2) * expected_values_distance + result


def histogram_matching_distance(hist1, hist2):
  def value_at_point(histogram, point):
    if histogram.has_key(point):
      return histogram[point]
    return 0

  def inner_histogram_matching_distance(hist1, hist2,
                                        colour_num=ColorValueTransform.rgb_to_number((255, 255, 255)) + 1):
    hist1_dict = dict(hist1)
    hist2_dict = dict(hist2)
    result = 0.0

    for point in xrange(colour_num):
      i = value_at_point(hist1_dict, point)
      j = value_at_point(hist2_dict, point)
      result += pow(i - j, 2) / (i + j + 0.0)
    return result / 2.0

  return inner_histogram_matching_distance(hist1, hist2)


def show(statistic):
  print "<ul>"
  print "<li><img src=\"" + statistic.path + "\"></li>"
  print "<li>expectation_value = ", statistic.expectation_value, "</li>"
  print "<li>dispersion = ", statistic.dispersion, "</li>"
  print "<li>standard_deviation = ", statistic.standard_deviation, "</li>"
  print "<li>main colors"
  for c in statistic.main_colors:
    #hex_color = ColorValueTransform.hsv_to_hex_string(ColorValueTransform.number_to_hsv(c))
    print "<p style=\"background-color: " + ColorValueTransform.rgb_to_hex_string(c) + "\">&nbsp</p>"
  print "</li>"

  print "</ul>"
  print


def process(img_id):
  img_path = "test_images/" + str(img_id) + ".jpeg"
  return ImgStatisticCounter(path=img_path)

if __name__ == '__main__':
  max_idx = 102

  ref_image_path = "test_images/ref.jpeg"
  ref_statistic = ImgStatisticCounter(path=ref_image_path)

  print "<div><h3>Reference image:</h3>"
  print "<img src=\"" + ref_image_path + "\">"
  print "</div>"
  print
  print

  statistics = [process(i) for i in xrange(max_idx)]
  statistics.sort(key=lambda x: x.distance(ref_statistic))
  for i in xrange(max_idx):
    show(statistics[i])