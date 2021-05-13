"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    # Third party urls
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Our urls
    path("accounts/", include("registration.urls")),
    path("courses/", include("course.urls")),
    path("documents/", include("document.urls")),
    path("videos/", include("video.urls")),
    path("cribs/", include("cribs.urls")),
    path("email_notices/", include("email_notices.urls")),
    path("discussion_forum/", include("discussion_forum.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        # Schema & docs
        path(
            "schema/",
            get_schema_view(
                title="BodhiTree", description="API for BodhiTree", version="1.0.0"
            ),
            name="openapi-schema",
        ),
        path("docs/", include_docs_urls(title="BodhiTree")),
        # Debug ttolbar
        path("__debug__/", include(debug_toolbar.urls)),
    ]
