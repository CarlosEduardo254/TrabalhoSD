create table medico
(
    id_med         bigint auto_increment
        primary key,
    nome_med       varchar(50) not null,
    especialidade    varchar(50) not null,
    crm varchar(20),
    telefone varchar(20) not null,
    email varchar(50) not null,
    senha varchar(255) not null,
    atend_inicio time,
    atend_fim time
);

create table paciente
(
	 id_usuario   bigint auto_increment
        primary key,
    nome         varchar(50) not null,
    problema varchar(255) not null,
    telefone varchar(20) not null,
    email        varchar(50) not null,
    senha varchar(255) not null
);

create table recepcionista
(
	 id_recep   bigint auto_increment
        primary key,
    nome         varchar(50) not null,
    telefone varchar(20) not null,
    email        varchar(50) not null,
    senha        varchar(50) not null
);

create table administradores
(
	 id_adm   bigint auto_increment
        primary key,
    nome         varchar(50) not null,
    telefone varchar(20) not null,
    email        varchar(50) not null,
    senha varchar(255) not null
);

create table consulta (
    id_consulta bigint auto_increment primary key,
    id_paciente bigint not null,
    id_medico bigint not null,
    data_consulta date not null,
    horario_consulta time not null,
    status varchar(25) default 'Aguardando Pagamento',
    foreign key (id_paciente) references paciente(id_usuario),
    foreign key (id_medico) references medico(id_med)
);

create table pagamento (
    id_pagamento bigint auto_increment primary key,
    id_consulta bigint not null unique,
    valor decimal(10, 2), 
    forma_pagamento varchar(30), 
    status_validacao varchar(20) default 'PENDENTE',
    foreign key (id_consulta) references consulta(id_consulta)
);