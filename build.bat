::图片转储
pyrcc5 -o images.py images.qrc

::编译可执行程序
pyinstaller -F -w --icon="image/icon.ico" change_fps.py