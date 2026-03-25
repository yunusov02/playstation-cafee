# playstation-cafee
Playstation cafee management Desktop Application


# Project  Structure

```
playstation_cafe/
├── main.py
├── config.py
├── database.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── playstation.py
│   ├── joystick.py
│   ├── session.py
│   └── session_segment.py
├── controllers/
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── playstation_controller.py
│   ├── session_controller.py
│   ├── joystick_controller.py
│   └── report_controller.py
├── views/
│   ├── __init__.py
│   ├── main_window.py
│   ├── login_dialog.py
│   ├── dashboard_widget.py
│   ├── playstation_card.py
│   ├── session_dialogs.py
│   ├── reports_widget.py
│   ├── settings_widget.py
│   └── management_widget.py
├── utils/
│   ├── __init__.py
│   ├── styles.py
│   ├── helpers.py
│   └── sound_manager.py
└── resources/
    └── sounds/
        └── timeout.wav
```