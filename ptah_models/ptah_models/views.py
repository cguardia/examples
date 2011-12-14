import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import form, cms

from ptah_models import models

# logger, check Debug Toolbar logging section or stdout
log = logging.getLogger(__name__)


class Telephone(form.Regex):
    """ An example validator.  See ptah.form.validators for more info."""

    def __init__(self, msg=None):
        log.info('Constructing a Telephone field validator')
        if msg is None:
            msg = "Invalid telephone number"
        super(Telephone, self).__init__(
            u'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$', msg=msg)


# This is a "class view", you do not need to use a class for your
# view. You can use a Function view as provided below.

@view_config(renderer='ptah_models:templates/homepage.pt', route_name='root')
class HomepageView(object):
    """ Homepage view """

    def __init__(self, request):
        self.request = request
        ptah.include(request, 'bootstrap')
        ptah.include(request, 'bootstrap-js')

    def get_links(self):
        return ptah.Session.query(models.Link)

    def __call__(self):
        return {'rendered_includes': ptah.render_includes(self.request),
                'rendered_messages': ptah.render_messages(self.request)}


# This is a "function view", you do not need to use a function for your
# view.  You can use a Class view as provided above.

@view_config(renderer='templates/contact-us.pt', route_name='contact-us')
def contact_us(context, request):
    contactform = form.Form(context, request)
    contactform.fields = form.Fieldset(

        form.TextField(
            'fullname',
            title = u'First & Last Name'),

        form.TextField(
            'phone',
            title = u'Telephone number',
            description=u'Please provide telephone number',
            validator = Telephone()),

        form.TextField(
            'email',
            title = u'Your email',
            description = u'Please provide email address.',
            validator = form.Email()),

        form.TextAreaField(
            'subject',
            title = u'How can we help?',
            missing = u''), # field use this value is request doesnt contain
                            # field value, effectively field is required
                            # if `missing` is not specified
        )

    # form actions
    def cancelAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()

        if errors:
            form.message(errors, 'form-error')
            return

        # form.context is ...
        form.context.fullname = data['fullname']
        form.context.phone = data['phone']
        form.context.email = data['email']
        form.context.subject = data['subject']

        # You would add any logic/database updates/insert here.
        # You would probably also redirect.

        log.info('The form was updated successfully')
        form.message('The form was updated successfully')

    contactform.label = u'Contact us'
    contactform.buttons.add_action('Update', action=updateAction)
    contactform.buttons.add_action('Cancel', action=cancelAction)

    # form default values
    contactform.content = {}

    # prepare form
    result = contactform.update()
    if isinstance(result, HTTPFound):
        return result

    # render form into HTML
    rendered_form = contactform.render()

    # query for links to populate links box
    links = ptah.Session.query(models.Link)

    #include library dependencies
    ptah.include(request, 'bootstrap')

    # render all the included libraries into html
    rendered_includes = ptah.render_includes(request)

    # render messages
    rendered_messages = ptah.render_messages(request)

    return {'links': links,
            'rendered_form': rendered_form,
            'rendered_messages': rendered_messages,
            'rendered_includes': rendered_includes}


@view_config(renderer='ptah_models:templates/edit.pt',
             context=models.Link,
             route_name='edit-links')
def edit_link(context, request):
    linkform = form.Form(context,request)
    linkform.fields = models.Link.__type__.fieldset

    def backAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()
        if errors:
            form.message(errors, 'form-error')
            return
        form.context.title = data['title']
        form.context.href = data['href']
        form.context.color = data['color']
        form.message('Link has been updated.')

    linkform.label = u'Edit link'
    linkform.buttons.add_action('Update', action=updateAction)
    linkform.buttons.add_action('Back', action=backAction)
    linkform.content = {'title':context.title,
                        'href':context.href,
                        'color':context.color}

    result = linkform.update() # prepare form for rendering
    if isinstance(result, HTTPFound):
        return result

    rendered_form = linkform.render()

    ptah.include(request, 'bootstrap')
    rendered_includes = ptah.render_includes(request)

    return {'links': cms.Session.query(models.Link),
            'rendered_form': rendered_form,
            'rendered_includes': rendered_includes,
            'rendered_messages': ptah.render_messages(request)}


@view_config(renderer='ptah_models:templates/edit.pt',
             route_name='add-link')
def add_link(context, request):
    linkform = form.Form(context,request)
    linkform.fields = models.Link.__type__.fieldset

    def cancelAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()
        if errors:
            form.message(errors, 'form-error')
            return

        link = models.Link(title = data['title'],
                           href = data['href'],
                           color = data['color'])
        ptah.Session.add(link)

        form.message('Link has been created.')
        return HTTPFound(location='/')

    linkform.label = u'Add link'
    linkform.buttons.add_action('Add', action=updateAction)
    linkform.buttons.add_action('Cancel', action=cancelAction)

    result = linkform.update() # prepare form for rendering
    if isinstance(result, HTTPFound):
        return result

    rendered_form = linkform.render()

    ptah.include(request, 'bootstrap')
    rendered_includes = ptah.render_includes(request)

    return {'links': cms.Session.query(models.Link),
            'rendered_form': rendered_form,
            'rendered_includes': rendered_includes,
            'rendered_messages': ptah.render_messages(request)}
