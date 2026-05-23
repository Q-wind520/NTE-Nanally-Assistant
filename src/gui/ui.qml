// import声明导入了一个指定的模块版本
import QtQuick
import QtQuick.Controls

// 在QML中，元素是通过大括号{}内的属性来配置的。
Item {
    width: 800                                                                  // Item的宽度
    height: 600                                                                 // Item的高度
    visible: true                                                               // 显示Item

    // 创建一个矩形
    Rectangle {
        id: rectangle1Id                                                        // 矩形的id
        x: 100                                                                  // 矩形所在窗口的横坐标
        y: 100                                                                  // 矩形所在窗口的纵坐标
        width: 100                                                              // 矩形的宽
        height: 100                                                             // 矩形的高
    
        color: "#FFCCCC"                                                        // 矩形的填充颜色
    }

    // 创建一个矩形
    Rectangle {
        x: rectangle1Id.x + rectangle1Id.width + 100                            // 矩形所在窗口的横坐标
        y: rectangle1Id.y                                                       // 矩形所在窗口的纵坐标
        width: rectangle1Id.width                                               // 矩形的宽
        height: rectangle1Id.height                                             // 矩形的高
    
        color: rectangle1Id.color                                               // 矩形的填充颜色
    }

    Button {
        id: buttonId
        width: 120                                                              // 按钮的宽
        height: 60                                                              // 按钮的高
        
        // 使用锚点（anchors）系统来定位文本元素，这里中心的锚点定位到其父元素的中心
        anchors.centerIn: parent

        text: "点击改变矩形颜色"                                                           // 按钮的文本

        // 按钮点击时触发信号
        onClicked: {
            // 改变矩形1的颜色
            rectangle1Id.color = Qt.rgba(Math.random(), Math.random(), Math.random(), 1)
        }
    }
}
