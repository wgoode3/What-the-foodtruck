from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.home),
	url(r'^results$', views.results),
	url(r'^user$', views.user),
	url(r'^register$', views.register),
	url(r'^login$', views.login),
	url(r'^logout$', views.logout),
	url(r'^addtruck$', views.addtruck),
	url(r'^add$', views.add),
	url(r'^truck/(?P<id>\d+)$', views.truck),
	url(r'^edittruck/(?P<id>\d+)$', views.edittruck),
	url(r'^edit/(?P<id>\d+)$', views.edit),
	url(r'^rating/(?P<id>\d+)$', views.rating),
	url(r'^update$', views.update),
	url(r'^reset$', views.reset),
]