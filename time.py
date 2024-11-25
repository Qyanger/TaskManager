from datetime import datetime
from typing import List, Dict
import time
import os
import sys
import json 

#有关数据方面的东西都放在最前面
#-----之间写的是类

# 用户账户数据 (简单的模拟用户数据库)

USER_DATABASE = {
    "admin": "admin123",
    "user1": "password1",
    "user2": "password2",
    "1":"1"#for test
    # "...": "..."
}


# 任务类----------------------------------------------------
class Task:
    def __init__(self, taskID: int, title: str, description: str):
        """
        初始化任务类
        :param taskID: 任务ID
        :param title: 任务标题
        :param description: 任务描述
        """
        self.taskID = taskID
        self.title = title
        self.description = description

        self.subtasks: List[str] = []  # 子任务列表
        self.resources: List[str] = []  # 资源列表

    def AddTask(self, title: str, description: str):
        """添加任务的标题和描述"""
        self.title = title
        self.description = description

    def AddSubtask(self, subtask: str):
        """添加子任务"""
        self.subtasks.append(subtask)

    def AddResource(self, resource: str):
        """添加资源"""
        self.resources.append(resource)

    def GetTaskDetails(self):
        """获取任务的详细信息"""
        return {
            "taskID": self.taskID,
            "title": self.title,
            "description": self.description,
            "subtasks": self.subtasks,
            "resources": self.resources,
        }

#-----------------------------------------------------

# 任务存储仓库类------------------------------------------------
class TaskRepository:
    def __init__(self, storage_file="tasks.json"):
        """
        初始化任务存储仓库
        :param storage_file: 用于持久化任务的存储文件
        """
        self.storage_file = storage_file
        self.user_tasks = {}  # 用户任务映射，键为用户名，值为该用户的任务字典
        self._load_tasks()

    def _load_tasks(self):
        """从存储文件加载任务"""
        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
                self.user_tasks = {
                    user: {int(taskID): Task(**task) for taskID, task in tasks.items()}
                    for user, tasks in data.items()
                }
            print("任务数据加载成功！")
        except FileNotFoundError:
            print("未找到任务数据文件，将创建新文件...")
        except json.JSONDecodeError:
            print("任务数据文件格式错误，未加载任何任务。")

    def _save_tasks(self):
        """将任务保存到存储文件"""
        with open(self.storage_file, "w") as f:
            data = {
                user: {taskID: vars(task) for taskID, task in tasks.items()}
                for user, tasks in self.user_tasks.items()
            }
            json.dump(data, f, indent=4)
        print("任务数据保存成功！")

    def add_task(self, user: str, task: Task):
        """
        为指定用户添加任务
        :param user: 用户名
        :param task: Task 对象
        """
        if user not in self.user_tasks:
            self.user_tasks[user] = {}
        if task.taskID in self.user_tasks[user]:
            print(f"任务ID {task.taskID} 已存在，无法重复添加！")
        else:
            self.user_tasks[user][task.taskID] = task
            self._save_tasks()
            print(f"任务 {task.title} 添加成功！")

    def get_task(self, user: str, taskID: int):
        """
        获取用户的任务
        :param user: 用户名
        :param taskID: 任务ID
        :return: Task 对象或 None
        """
        if user in self.user_tasks and taskID in self.user_tasks[user]:
            return self.user_tasks[user][taskID]
        print(f"用户 {user} 的任务ID {taskID} 不存在！")
        return None

    def delete_task(self, user: str, taskID: int):
        """
        删除用户的任务
        :param user: 用户名
        :param taskID: 任务ID
        """
        if user in self.user_tasks and taskID in self.user_tasks[user]:
            del self.user_tasks[user][taskID]
            self._save_tasks()
            print(f"任务 {taskID} 删除成功！")
        else:
            print(f"用户 {user} 的任务ID {taskID} 不存在！")

    def list_tasks(self, user: str):
        """
        列出用户的所有任务
        :param user: 用户名
        """
        if user not in self.user_tasks or not self.user_tasks[user]:
            print(f"用户 {user} 当前没有任务！")
        else:
            print(f"用户 {user} 的任务列表：")
            for taskID, task in self.user_tasks[user].items():
                print(f"任务ID: {taskID} | 标题: {task.title} | 描述: {task.description}")
#-----------------------------------------------------


# 时间线类-----------------------------------------------------
class Timeline:
    def __init__(self, timelineID: int):
        """
        初始化时间线类
        :param timelineID: 时间线ID
        """
        self.timelineID = timelineID
        self.tasks: List[Task] = []  # 时间线中的任务列表
        self.ddlReminder: datetime = None  # 截止日期提醒

    def AddTaskToTimeline(self, task: Task):
        """将任务添加到时间线"""
        self.tasks.append(task)

    def SetDDLReminder(self, ddl: datetime):
        """设置截止日期提醒"""
        self.ddlReminder = ddl

    def GetTimeline(self):
        """获取时间线的详细信息"""
        return {
            "timelineID": self.timelineID,
            "tasks": [task.GetTaskDetails() for task in self.tasks],
            "ddlReminder": self.ddlReminder.strftime("%Y-%m-%d %H:%M:%S") if self.ddlReminder else None,
        }
    
    def PrintTimeline(self):
        """
        打印时间线，以竖线的形式展示任务
        """
        print("时间线：")
        print("|")
        for task, task_time in self.tasks:
            print(f"|  {task_time} | 任务ID: {task.taskID} | 简介: {task.description}")
            print("|")
        if not self.tasks:
            print("|  （当前没有任务）")
        print("|")

#-----------------------------------------------------

# 权限类-----------------------------------------------------
class Permission:
    def __init__(self, userID: int, role: str):
        """
        初始化权限类
        :param userID: 用户ID
        :param role: 用户角色
        """
        self.userID = userID
        self.role = role
        self.permissions: List[str] = []  # 权限列表

    def AssignWorker(self, userID: int):
        """分配用户ID"""
        self.userID = userID

    def SetAdminPermissions(self, userID: int):
        """设置管理员权限"""
        if userID == self.userID:
            self.role = "Admin"
            self.permissions = ["Create Task", "Edit Task", "Delete Task", "Manage Permissions"]
        else:
            print(f"用户ID {userID} 不匹配，无法设置管理员权限。")

    def GetPermissions(self, userID: int):
        """获取用户权限信息"""
        if userID == self.userID:
            return {"userID": self.userID, "role": self.role, "permissions": self.permissions}
        else:
            return {"message": "未找到此用户的权限信息。"}
#-----------------------------------------------------

# 资源管理类--------------------------------------
class ResourceManager:
    def __init__(self):
        """初始化资源管理类"""
        self.resources: Dict[int, Dict] = {}  # 资源存储，键为资源ID

    def IntegrateResources(self, resourceID: int, resourceType: str, relatedTasks: List[Task]):
        """整合资源并与任务关联"""
        self.resources[resourceID] = {
            "resourceType": resourceType,
            "relatedTasks": [task.GetTaskDetails() for task in relatedTasks],
        }

    def CategorizeResource(self, resourceID: int, resourceType: str):
        """分类资源"""
        if resourceID in self.resources:
            self.resources[resourceID]["resourceType"] = resourceType
        else:
            print(f"资源ID {resourceID} 未找到。")

    def GetResourceDetails(self, resourceID: int):
        """获取资源的详细信息"""
        return self.resources.get(resourceID, {"message": "资源未找到。"})
#-----------------------------------------------------

#群组类的建立--------------------------------------
class Group:
    def __init__(self, groupID: int, groupName: str, owner: str):
        """
        初始化群组
        :param groupID: 群组ID
        :param groupName: 群组名称
        :param owner: 群组创建者用户名
        """
        self.groupID = groupID
        self.groupName = groupName
        self.owner = owner
        self.members = [owner]  # 成员列表，初始包含创建者
        self.tasks = []  # 群组共享的任务列表

    def add_member(self, username: str):
        """添加成员到群组"""
        if username not in self.members:
            self.members.append(username)
            print(f"用户 {username} 已加入群组 {self.groupName}！")
        else:
            print(f"用户 {username} 已经是群组 {self.groupName} 的成员！")

    def add_task(self, task: Task):
        """将任务共享到群组"""
        self.tasks.append(task)
        print(f"任务 {task.title} 已共享到群组 {self.groupName}！")

    def list_tasks(self):
        """列出群组中的所有任务"""
        if not self.tasks:
            print(f"群组 {self.groupName} 中没有共享任务！")
        else:
            print(f"群组 {self.groupName} 的任务列表：")
            for task in self.tasks:
                print(f"任务ID: {task.taskID} | 标题: {task.title} | 描述: {task.description}")
#-----------------------------------------------------

#群组管理器----------------------------------------
class GroupManager:
    def __init__(self):
        """初始化群组管理器"""
        self.groups = {}  # 存储所有群组，键为群组ID，值为Group对象

    def create_group(self, groupID: int, groupName: str, owner: str):
        """创建群组"""
        if groupID in self.groups:
            print(f"群组ID {groupID} 已存在，无法重复创建！")
        else:
            self.groups[groupID] = Group(groupID, groupName, owner)
            print(f"群组 {groupName} 创建成功！")

    def join_group(self, groupID: int, username: str):
        """加入群组"""
        if groupID in self.groups:
            self.groups[groupID].add_member(username)
        else:
            print(f"群组ID {groupID} 不存在！")

    def share_task_to_group(self, groupID: int, task: Task):
        """将任务共享到群组"""
        if groupID in self.groups:
            self.groups[groupID].add_task(task)
        else:
            print(f"群组ID {groupID} 不存在！")

    def list_group_tasks(self, groupID: int):
        """列出群组中的所有任务"""
        if groupID in self.groups:
            self.groups[groupID].list_tasks()
        else:
            print(f"群组ID {groupID} 不存在！")
#---------------------------------------------------


def clear_input_buffer():
    """清除终端的输入缓冲区，避免倒计时期间按键被读取"""
    if os.name == 'nt': 
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


# 登录函数
def login():
    print("欢迎登录任务管理系统！")
    attempts = 3  # 最大尝试次数
    while attempts > 0:
        username = input("请输入用户名：")
        password = input("请输入密码：")
        # 检查是否为空输入
        if not username or not password:
            print("用户名或密码不能为空，请重新输入！")
            continue  # 空输入不算尝试次数
 
        if username in USER_DATABASE and USER_DATABASE[username] == password:
            print(f"\n登录成功！欢迎您，{username}！\n")
            return username  # 返回成功登录的用户名
        else:
            attempts -= 1
            print(f"用户名或密码错误！您还有 {attempts} 次尝试机会。")

        # 超过最大尝试次数，限制 30 秒 
        if attempts == 0:
            print("多次登录失败，请稍后再试（30秒）。")
            for i in range(30, 0, -1):  # 显示倒计时
                print(f"\r请等待 {i} 秒...", end="")
                time.sleep(1)
            print("\n")  # 倒计时结束后换行
            clear_input_buffer()
            attempts = 3  # 重置
    return username


def main():
    # 初始化任务存储仓库
    task_repo = TaskRepository(storage_file="tasks.json")  # 任务持久化文件
    group_manager = GroupManager()  # 初始化群组管理器
    
    # 登录界面
    current_user = login()

    # 初始化对象
    timeline = Timeline(timelineID=1)  # 初始化时间线
    permission = Permission(userID=101, role="User")  # 默认用户为普通用户
    resource_manager = ResourceManager()  # 初始化资源管理

    print(f"---------欢迎使用任务管理系统，{current_user}！------------")
    while True:
        print("\n请选择操作：")
        print("1. 创建任务")
        print("2. 添加子任务")
        print("3. 添加资源")
        print("4. 查看任务详情")
        print("5. 添加任务到时间线")
        print("6. 设置DDL提醒")
        print("7. 查看时间线详情")
        print("8. 设置用户权限")
        print("9. 整合资源")
        print("10. 查看资源详情")
        print("11. 打印时间线")
        print("12. 列出所有任务")
        print("13. 创建群组")
        print("14. 加入群组")
        print("15. 共享任务到群组")
        print("16. 查看群组任务")
        print("0. 退出")
        choice = input("请输入操作编号：")

        if choice == "1":
            taskID = int(input("请输入任务ID："))
            title = input("请输入任务标题：")
            description = input("请输入任务描述：")
            task = Task(taskID=taskID, title=title, description=description)
            task_repo.add_task(current_user, task)  # 添加任务到当前用户的存储中
            print(f"任务 {title} 创建成功！")

        elif choice == "2":
            taskID = int(input("请输入任务ID："))
            task = task_repo.get_task(current_user, taskID)
            if task:
                subtask = input("请输入子任务内容：")
                task.AddSubtask(subtask)
                task_repo._save_tasks()  # 保存更新后的任务
                print(f"子任务 '{subtask}' 添加成功！")
            else:
                print("任务ID不存在！")

        elif choice == "3":
            taskID = int(input("请输入任务ID："))
            task = task_repo.get_task(current_user, taskID)
            if task:
                resource = input("请输入资源名称：")
                task.AddResource(resource)
                task_repo._save_tasks()  # 保存更新后的任务
                print(f"资源 '{resource}' 添加成功！")
            else:
                print("任务ID不存在！")

        elif choice == "4":
            taskID = int(input("请输入任务ID："))
            task = task_repo.get_task(current_user, taskID)
            if task:
                print("任务详情：")
                print(task.GetTaskDetails())
            else:
                print("任务ID不存在！")

        elif choice == "5":
            taskID = int(input("请输入任务ID："))
            task = task_repo.get_task(current_user, taskID)
            if task:
                timeline.AddTaskToTimeline(task)
                print(f"任务 {task.title} 已添加到时间线！")
            else:
                print("任务ID不存在！")

        elif choice == "6":
            try:
                ddl = input("请输入DDL（格式：YYYY-MM-DD HH:MM:SS）：")
                ddl_date = datetime.strptime(ddl, "%Y-%m-%d %H:%M:%S")
                timeline.SetDDLReminder(ddl_date)
                print("DDL提醒设置成功！")
            except ValueError:
                print("日期格式错误，请重新输入！")

        elif choice == "7":
            print("时间线详情：")
            print(timeline.GetTimeline())

        elif choice == "8":
            userID = int(input("请输入用户ID："))
            role = input("请输入用户角色（User 或 Admin）：")
            permission.AssignWorker(userID)
            if role == "Admin":
                permission.SetAdminPermissions(userID)
            print(f"用户 {userID} 的角色已设置为 {role}！")
            print("权限详情：")
            print(permission.GetPermissions(userID))

        elif choice == "9":
            resourceID = int(input("请输入资源ID："))
            resourceType = input("请输入资源类型：")
            related_task_ids = input("请输入关联任务ID（以逗号分隔）：").split(",")
            related_tasks = []
            for task_id in related_task_ids:
                task_id = int(task_id.strip())
                task = task_repo.get_task(current_user, task_id)
                if task:
                    related_tasks.append(task)
                else:
                    print(f"任务ID {task_id} 不存在，跳过。")
            resource_manager.IntegrateResources(resourceID, resourceType, related_tasks)
            print("资源整合成功！")

        elif choice == "10":
            resourceID = int(input("请输入资源ID："))
            print("资源详情：")
            print(resource_manager.GetResourceDetails(resourceID))

        elif choice == "11":
            timeline.PrintTimeline()

        elif choice == "12":
            task_repo.list_tasks(current_user)  # 列出当前用户的所有任务

        elif choice == "13":  # 创建群组
            groupID = int(input("请输入群组ID："))
            groupName = input("请输入群组名称：")
            group_manager.create_group(groupID, groupName, current_user)

        elif choice == "14":  # 加入群组
            groupID = int(input("请输入群组ID："))
            group_manager.join_group(groupID, current_user)

        elif choice == "15":  # 共享任务到群组
            groupID = int(input("请输入群组ID："))
            taskID = int(input("请输入要共享的任务ID："))
            task = task_repo.get_task(current_user, taskID)
            if task:
                group_manager.share_task_to_group(groupID, task)
            else:
                print("任务ID不存在！")

        elif choice == "16":  # 查看群组任务
            groupID = int(input("请输入群组ID："))
            group_manager.list_group_tasks(groupID)

        elif choice == "0":
            print("感谢使用任务管理系统，再见！")
            break

        else:
            print("无效的操作编号，请重新输入！")



if __name__ == "__main__":
    main()
