# TABLE++

- [TABLE++](#table)
    - [Login page](#login-page)
    - [User model](#user-model)
      - [Update user info page](#update-user-info-page)
      - [Update user's groups](#update-users-groups)
      - [Update user's permissions](#update-users-permissions)
    - [User groups](#user-groups)
      - [User groups permissions](#user-groups-permissions)
    - [Roles](#roles)
      - [Role list](#role-list)
      - [Role settings](#role-settings)
    - [Tables](#tables)
      - [Table list](#table-list)
      - [Table creation](#table-creation)
      - [Object list](#object-list)
    - [Logs](#logs)
  - [⭐ Credits](#-credits)

This application was created to simplify and speed up accounting in small companies. 

The main models are tables and their columns, users, groups, permissions and roles. Each user contains information about the corresponding employee (their name, role, email, password, whether they are a super user). 

A system of permissions is also implemented, with the help of which the user is given the opportunity or is prohibited from performing certain actions actions.

The main feature of our application is the ease of adding new entries. To do this, we enter the necessary data in a special window, and they are automatically added. 

### Login page
On the login page, you must enter the username and password provided to you by the administrator
<center><img src="./assets/login.png" width=85%></center>

### User model
#### Update user info page
After login you will be automatically sent to your user's settings page.
<center><img src="./assets/update.png" width=85%></center>

If you have super admin rights, you can change any item in any user's data, as well as delete any user.
<center><img src="./assets/not_super_update_form.png" width=85%></center>

You may notice that if you log in from a non-super user account, you won't be able to change anything but your password and won't be able to access other users' profiles.
<center><img src="./assets/no_acces_to_user.png" width=85%></center>

#### Update user's groups
On this page, you can add users to groups or remove them from them. Only super users have an access to this page.
<center><img src="./assets/change_groups.png" width=85%></center>

#### Update user's permissions
On this page, you can grant permissions to each user individually. Such permissions are in higher priority than group permissions. Only super users have an access to this page.
<center><img src="./assets/user_perms.png" width=85%></center>

### User groups 
Here you can view the list of groups. 
<center><img src="./assets/groups_list.png" width=85%></center>

Only super users can access the settings of each group.
<center><img src="./assets/update_group.png" width=85%></center>

#### User groups permissions
Each group can be granted permissions that will be guaranteed for each user in this group. Only super-users can access this page.
<center><img src="./assets/group_perms.png" width=85%></center>


### Roles
#### Role list
Here you can see a list of roles.
<center><img src="./assets/role_list.png" width=85%></center>

#### Role settings
You can change a name of the role. Only super users have an access to this page.
<center><img src="./assets/role_update.png" width=85%></center>

### Tables
#### Table list
When we go to tables, we will see a list of existing tables.
<center><img src="./assets/tables.png" width=85%></center>

#### Table creation
Let's try creating a new table, in addition to the above, we can also specify the limits for each field, and how to filter it in order to find the relevant data.
<center><img src="./assets/create_table.png" width=85%></center>

As we can see, we cannot go beyond these limits.
<center><img src="./assets/add_object_err.png" width=85%></center>

#### Object list
This displays a list of entries. It is also possible to export data to an excel spreadsheet
To edit an object you have to press on its index. To view object from relationship field you have to press on this field text.
<center><img src="./assets/objects_list.png" width=85%></center>

We can edit information about each table or its objects.

### Logs
Implemented logging of actions, as you can see, the creation of our new object has been added to the log table
<center><img src="./assets/logs.png" width=85%></center>

## ⭐ Credits
Sincere appreciation to the following people who helped with development of this web application.

[Veronika Sazonova](https://github.com/veronasaz)

[Sofia Sydorchuk](https://github.com/Sydorchuksofiaa)

[Valihurskyi Anton](https://github.com/BlueSkyAndSomeCurses)

[Maksym Bug](https://github.com/Zhukowych)

[Mentor: Victor Muryn](https://github.com/hellcastter)

