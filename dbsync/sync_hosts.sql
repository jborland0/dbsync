create table sync_hosts
(
	id int not null primary key,
    lastsync datetime,
    inprogress datetime
);
