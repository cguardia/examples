import ptah
import ptahcms
from ptah import view, manage, auth_service

from ptah_minicms.root import SiteRoot
from ptah_minicms.actions import CATEGORY


ptah.layout.register(
    'ptah-page', SiteRoot, parent='workspace',
    renderer='ptah_minicms:templates/layout-ptahpage.pt')


@ptah.layout(
    'page', SiteRoot,
    renderer='ptah_minicms:templates/layout-page.pt')

class PageLayout(ptah.View):
    """ override 'page' layout

    layer - identifier, import order does matter, last imported wins
    """


@ptah.layout(
    'workspace', SiteRoot, parent='page',
    renderer='ptah_minicms:templates/layout-workspace.pt')

class WorkspaceLayout(ptah.View):
    """ same as PageLayout, it uses 'page' as parent layout """

    def update(self):
        self.user = ptah.auth_service.get_current_principal()
        self.ptahManager = manage.check_access(
            ptah.auth_service.get_userid(), self.request)
        self.isAnon = self.user is None


@ptah.layout(
    '', ptahcms.Content, parent="workspace",
    renderer="ptah_minicms:templates/layout-content.pt")
class ContentLayout(ptah.View):
    """ Content layout """

    def update(self):
        self.actions = ptah.list_uiactions(
            self.context, self.request, CATEGORY)
