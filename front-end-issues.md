# 前端存在的问题

1. 页面元素不对齐
2. 用 空格 来实现对齐而不是 css
3. 结构设计混乱

## 前端设计

数据

+ `Department` 部门 service
+ `UserInfo` 通讯录登陆信息 service
  + `logined` 是否登陆 bool
  + `userName` 用户名 string
+ `StaffManager` 员工信息 service
+ `StaffList` 员工信息列表 controller
  + `staffFilter` 筛选条件 function
  + `staffData` 员工信息 array<Staff>
  + `selected` 被勾选的员工信息 array<Staff>
+ `StaffEditor` 员工信息编辑 controller
  + `action` 当前正在执行的动作 `enum<add, edit>`
  + `editingStaff` 框定的员工信息
+ `StaffList` html
+ `StaffModal` html

