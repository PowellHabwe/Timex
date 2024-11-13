
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),

    path('dashboard/', views.user_dashboard, name='user_dashboard'),


    path('location/', views.location, name='location'),
    # path('nearest_vehicles/', views.get_nearby_vehicles, name='get_nearby_hospitals'),
    path('display_nearest_vehicles/', views.display_nearest_vehicles, name='display_nearest_vehicles'),
    path('user_admin/', views.user_admin_page, name='user_admin_page'),
    # path('doc_admin/', views.driver_admin_page, name='doc_admin_page'),
    path('drivers/', views.drivers, name='drivers'),
    path('about/', views.about, name='about'),
    path('contact_us/', views.contact_us, name='contact_us'),
    
    path('plot_distance/<str:user_latitude>/<str:user_longitude>/<str:vehicle_latitude>/<str:vehicle_longitude>/', views.plot_distance, name='plot_distance'),
    
    # path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('driver_dashboard/', views.driver_dashboard, name='driver_dashboard'),


    path('store/<str:pk>/', views.vehicle_detail, name='vehicle_detail'),

    path('ride/<int:ride_id>/confirmation/', views.ride_confirmation, name='ride_confirmation'),


    # path('book_vehicle/<str:user_latitude>/<str:user_longitude>/<str:vehicle_latitude>/<str:vehicle_longitude>/', views.book_vehicle, name='book_vehicle'),
    path('book-vehicle/<str:vehicle_latitude>/<str:vehicle_longitude>/', views.book_vehicle, name='book_vehicle'),
    path('vehicle/update-status/<int:vehicle_id>/', views.update_vehicle_status, name='update_vehicle_status'),

    path('ride/mark-completed/<int:ride_id>/', views.mark_ride_completed, name='mark_ride_completed'),



] 