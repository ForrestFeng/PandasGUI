#导入Qt相关模块
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QTextEdit
from PyQt5.QtCore import Qt

#导入sys模块
import sys

#创建QApplication
app = QApplication(sys.argv)

#创建并设置MainWindow
main = QMainWindow()
main.setWindowTitle("DockWidget示例")
main.setCentralWidget(QTextEdit())
main.resize(640, 480)

#添加菜单
menu = main.menuBar()
file = menu.addMenu("&File")
file.addAction("&New")
file.addAction("&Open")
file.addAction("&Save")

#创建Dock1，利用setStyleSheet更改样式
dock1 = QDockWidget("Dock1")
dock1.setWidget(QTextEdit())
dock1.setStyleSheet(
    """
    /*设置边框和图标*/
    QDockWidget {
        border: 1px solid lightgray;
        //titlebar-close-icon: url(close.png);
        //titlebar-normal-icon: url(undock.png);
    }
    /*设置标题栏样式*/
    QDockWidget::title {
        text-align: left center; 
        background: lightgray;
        padding-left: 5px;
    }
    /*设置按钮样式*/
    QDockWidget::close-button, QDockWidget::float-button {
        border: 1px solid transparent;
        background: darkgray;
        padding: 0px;
    }
    /*鼠标在其上移动时按钮样式*/
    QDockWidget::close-button:hover, QDockWidget::float-button:hover {
        background: red;
    }
    /*按钮按下时样式*/
    QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {
        padding: 1px -1px -1px 1px;
    }
    """
    )

#创建Dock2，使用setFeatures函数设置只显示关闭按钮
dock2 = QDockWidget("Dock2")
dock2.setWidget(QTextEdit())
dock2.setFeatures(QDockWidget.DockWidgetClosable)

#创建Dock3，使用setFeatures函数设置竖向标题栏
dock3 = QDockWidget("Dock3", main)
dock3.setWidget(QTextEdit())
#dock3.setFeatures(QDockWidget.DockWidgetVerticalTitleBar)
dock3.setFeatures(QDockWidget.DockWidgetFloatable)

#添加到主窗体
# main.addDockWidget(Qt.LeftDockWidgetArea, dock1)
# main.addDockWidget(Qt.LeftDockWidgetArea, dock2)
#main.addDockWidget(Qt.LeftDockWidgetArea, dock3)
main.addDockWidget(Qt.BottomDockWidgetArea, dock3)

#使用Tab方式显示DockWidgets
# main.tabifyDockWidget(dock1, dock2)
# main.tabifyDockWidget(dock2, dock3)

#显示主窗体
main.show()

#进入循环，直到主窗体关闭
sys.exit(app.exec())
