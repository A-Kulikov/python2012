__author__ = 'ksenia'

import os

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

import formencode

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from pyramid.url import route_path

from .models import (
  DBSession,
  Image,
  )

from .database_manager import DBManager

import logging

logger = logging.getLogger('models')
logger.setLevel(logging.DEBUG)


@view_config(route_name='home', renderer='templates/home.pt')
def home_view(request):
  logger.info('home_view')
  return {
    'page_name': 'Home'
  }


class PictureUploadSchema(formencode.Schema):
  allow_extra_fields = True
  picture = formencode.validators.FieldStorageUploadConverter(not_empty=True)


@view_config(route_name='upload', renderer='templates/upload.pt')
def upload_view(request):
  logger.info("upload_view")
  form = Form(request, schema=PictureUploadSchema)
  message = ''

  if 'form_submitted' in request.POST:
    if form.validate():
      field = request.POST.get('picture')
      filename = field.filename
      content = field.value

      (_, extension) = os.path.splitext(filename)
      extension = extension.lower()
      logger.debug('Received file with extension "{0}"'.format(extension))
      if extension == '.jpeg' or extension == '.jpg':
        # Search
        image = DBManager.retrieve_image_by_name(filename)

        # If found then do nothing
        # Otherwise it should be processed and saved to database
        if image is None:
          # Call of processing function
          # Parameter: content
          # Returned dictionary:
          #   'histogram' (string)
          #   'expectation_value' (float)
          #   'dispersion' (float)
          #   'standard_deviation' (float)

          image_parameters = {
            'histogram': '',
            'expectation_value': 0.0,
            'dispersion': 0.0,
            'standard_deviation': 0.0
          }

          # image_parameters = image_processing_module.process_image(content)

          image = DBManager.create_image(
            filename=filename,
            content=content,
            histogram=image_parameters['histogram'],
            exp_value=image_parameters['expectation_value'],
            dispersion=image_parameters['dispersion'],
            std_dev=image_parameters['standard_deviation']
          )

        request.session['image'] = image
        return HTTPFound(location=route_path('result', request))

      else:
        message = 'red'

  return {
    'form': FormRenderer(form),
    'message': message,
    'page_name': 'Upload'
  }


class PictureChoosingSchema(formencode.Schema):
  allow_extra_fields = True
  picture = formencode.validators.NotEmpty()


@view_config(route_name='choose', renderer='templates/choose.pt')
def choose_view(request):
  logger.info("choose_view")
  form = Form(request, schema=PictureChoosingSchema)
  if form.validate():
    name = request.POST.get('picture')
    image = DBManager.retrieve_image_by_name(name=name)
    request.session['image'] = image
    return HTTPFound(location=route_path('result', request))

  return {
    'page_name': 'Choose',
    'form': FormRenderer(form),
    'images': DBManager.retrieve_all_images()
  }


@view_config(route_name='result', renderer='templates/result.pt')
def result_view(request):
  logger.info("result_view")
  image = request.session.get('image')
  if not image:
    return HTTPFound(location=route_path('home', request))

  # images = DBManager.retrieve_suitable_images()

  images = DBManager.retrieve_all_except_one(image_id=image['id'])

  return {
    'image': image,
    'images': images,
    'page_name': 'Result'
  }