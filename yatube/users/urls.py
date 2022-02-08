from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('logout/',
         LogoutView.as_view
         (template_name='users/logged_out.html',
          extra_context={'notification_title': 'Выход',
                         'notification_text': 'Вы вышли из своей учётной '
                         'записи. Ждём вас снова!'}
          ),
         name='logout'
         ),
    path('login/',
         LoginView.as_view
         (template_name='users/login.html',
          extra_context={'form_title': 'Войти на сайт',
                         'button_text': 'Войти',
                         'link': 'users:password_reset_form'}
          ),
         name='login'),
    path('signup/',
         views.SignUp.as_view
         (extra_context={'form_title': 'Зарегистрироваться',
                         'button_text': 'Зарегистрироваться'}
          ),
         name='signup'
         ),
    path('password_change/',
         PasswordChangeView.as_view
         (template_name='users/password_change_form.html',
          extra_context={'form_title': 'Изменить пароль',
                         'button_text': 'Изменить пароль'}
          ),
         name='password_change'),
    path('password_change/done/',
         PasswordChangeDoneView.as_view
         (template_name='users/password_change_done.html',
          extra_context={'notification_title': 'Пароль изменён',
                         'notification_text': 'Пароль изменён успешно'}
          ),
         name='password_change_done'),
    path('password_reset/',
         PasswordResetView.as_view
         (template_name='users/password_reset_form.html',
          extra_context={'form_title': 'Чтобы сбросить старый пароль — введите'
                         ' адрес электронной почты, под которым вы '
                         'регистрировались',
                         'button_text': 'Сбросить пароль'}
          ),
         name='password_reset_form'),
    path('password_reset/done/',
         PasswordResetDoneView.as_view
         (template_name='users/password_reset_done.html',
          extra_context={'notification_title': 'Отправлено письмо',
                         'notification_text': 'Проверьте свою почту, вам '
                         'должно прийти письмо со ссылкой для восстановления '
                         'пароля'}
          ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view
         (template_name='users/password_reset_confirm.html',
          extra_context={'form_title': 'Введите новый пароль',
                         'button_text': 'Назначить новый пароль',
                         'notification_title': 'Ошибка',
                         'notification_text': 'Ссылка сброса пароля содержит '
                         'ошибку или устарела.'}
          ),
         name='password_reset_confirm'),
    path('reset/done/',
         PasswordResetCompleteView.as_view
         (template_name='users/password_reset_complete.html',
          extra_context={'notification_title': 'Восстановление пароля '
                         'завершено',
                         'link': 'users:login',
                         'notification_text': 'Ваш пароль был сохранен. '
                         'Используйте его для входа'}
          ),
         name='password_reset_complete'),
]
