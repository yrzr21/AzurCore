from plugins.shortcut_creator.shortcut_creator_service import ShortcutCreatorService
from plugins.shortcut_creator.shortcut_creator_view import ShortcutCreatorView


class ShortcutCreatorController:
    """
    ui 与 service 的适配器，处理事件
    验证输入合法性
    """

    def __init__(self, view: ShortcutCreatorView, service: ShortcutCreatorService):
        self.view = view
        self.service = service

        # 连接UI事件
        view.create_requested.connect(self.on_create_requested)
        view.cancel_requested.connect(self.on_cancel_requested)

        # 连接服务事件
        service.task_started.connect(self.on_task_started)
        service.task_completed.connect(self.on_task_completed)
        service.error_occurred.connect(self.on_task_error)
        # 直接绑到 view
        service.progress_updated.connect(self.view.update_progress)

    # ui 事件
    def on_create_requested(self, data):
        """处理创建请求"""
        print("on_create_requested, data=",data)
        # 验证输入合法性
        validate = self.service.validate_input(
            data["target_dir"],
            data["file_paths"]
        )
        if not validate:
            return

        self.service.create_shortcuts(
            data["target_dir"],
            data["file_paths"]
        )

    def on_cancel_requested(self):
        """处理取消请求"""
        self.service.cancel_all()

    # 服务事件
    def on_task_started(self):
        """任务开始处理"""
        self.view.set_ui_state(busy=True)

    def on_task_completed(self, success, result):
        """任务完成处理"""
        print(f"result={result}")
        count = result
        print(f"count={count}")

        self.view.set_ui_state(busy=False)
        if success:
            self.view.show_message("消息", f"成功创建了{count}个快捷方式!")
        else:
            self.view.show_message("消息", "已取消")

    def on_task_error(self, message):
        """任务错误处理"""
        self.view.set_ui_state(busy=False)
        self.view.show_message("错误", message, True)
