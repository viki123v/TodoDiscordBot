create table projects(
    name varchar(200) NOT NULL,
    server_name varchar(200) NOT NULL,
    PRIMARY KEY (name,server_name)
);

create table tasks(
   name varchar(200) NOT NULL,
   server_name varchar(200) NOT NULL,
   project_name varchar(200) NOT NULL,
   assignee varchar(100),
   FOREIGN KEY (server_name,project_name) references projects(server_name,name),
   PRIMARY KEY (name,server_name,project_name)
);