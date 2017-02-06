from django.conf.urls import patterns, include, url

from integral_view.views.scheduler_cron_management import view_scheduled_jobs,download_cron_log,remove_cron_job,view_background_tasks,view_task_details, remove_background_task

from integral_view.views.ntp_management import configure_ntp_settings, view_ntp_settings

from integral_view.views.admin_auth  import login, logout, change_admin_password, view_email_settings, configure_email_settings, view_https_mode, edit_https_mode, reboot_or_shutdown, reload_manifest, reset_to_factory_defaults, flag_node, view_system_info

from integral_view.views.pki_management  import view_ssl_certificates, delete_ssl_certificate, create_self_signed_ssl_certificate, upload_ssl_certificate, known_hosts_ssh_keys, user_ssh_keys, upload_ssh_user_key, upload_ssh_host_key

from integral_view.views.common import show, dashboard,shell_access, view_backup

from integral_view.views.log_management import  download_log, rotate_log, view_rotated_log_list, view_rotated_log_file, edit_integral_view_log_level,download_sys_info,upload_sys_info, refresh_alerts, raise_alert, internal_audit, view_alerts, view_audit_trail, view_hardware_logs, view_log

from integral_view.views.cifs_share_management import view_cifs_shares, create_cifs_share, samba_server_settings, save_samba_server_settings, view_cifs_share, edit_cifs_share, delete_cifs_share, edit_auth_method 

from integral_view.views.folder_management import delete_ace, add_aces, edit_aces, modify_dir_permissions, create_dir, delete_dir, dir_manager, modify_dir_owner, get_dir_listing, view_dir_ownership_permissions, dir_contents

from integral_view.views.local_user_management import view_local_users, create_local_user, change_local_user_password, delete_local_user, view_local_user, edit_local_user_gid, view_local_groups, edit_local_user_group_membership, view_local_group, create_local_group, delete_local_group, modify_group_membership

from integral_view.views.nfs_share_management import view_nfs_shares, view_nfs_share, delete_nfs_share, create_nfs_share, edit_nfs_share

from integral_view.views.zfs_management import view_zfs_pools, view_zfs_pool, view_zfs_dataset, edit_zfs_dataset, delete_zfs_dataset, create_zfs_dataset, view_zfs_snapshots, create_zfs_snapshot, delete_zfs_snapshot, rename_zfs_snapshot, rollback_zfs_snapshot, create_zfs_pool, delete_zfs_pool, set_zfs_slog, remove_zfs_slog, scrub_zfs_pool, create_zfs_zvol, view_zfs_zvol, replace_disk, import_all_zfs_pools, add_zfs_spares, remove_zfs_spare, expand_zfs_pool, remove_zfs_quota, set_zfs_quota, export_zfs_pool, import_zfs_pool, schedule_zfs_snapshot, set_zfs_l2arc, remove_zfs_l2arc,create_remote_replication, view_disks,view_remote_replications, identify_disk, remove_remote_replication, modify_remote_replication, view_zfs_snapshot_schedules

#from zfs.zfs_management import view_zfs_pools, view_zfs_pool, view_zfs_dataset, edit_zfs_dataset, delete_zfs_dataset, create_zfs_dataset, view_zfs_snapshots, create_zfs_snapshot, delete_zfs_snapshot, rename_zfs_snapshot, rollback_zfs_snapshot, create_zfs_pool, delete_zfs_pool, set_zfs_slog

from integral_view.views.networking_management import view_interfaces, view_nic, view_bond, set_interface_state, edit_interface_address, create_bond, remove_bond, view_hostname, edit_hostname, view_dns_nameservers, edit_dns_nameservers,view_route, create_route,edit_route,delete_route, remove_vlan, create_vlan

from integral_view.views.services_management import view_services, change_service_status

from integral_view.views.ftp_management import configure_ftp, view_ftp_configuration, create_ftp_user_dirs

from integral_view.views.stgt_iscsi_management import view_targets, view_target, create_iscsi_target, delete_iscsi_target, add_iscsi_user_authentication, remove_iscsi_user_authentication, create_iscsi_lun, delete_iscsi_lun, add_iscsi_acl, remove_iscsi_acl

from integral_view.views.rsync_share_management import create_rsync_share,edit_rsync_share,view_rsync_shares,delete_rsync_share

from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'integral_view.views.home', name='home'),
    # url(r'^integral_view/', include('integral_view.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', login),
    url(r'^$', login),
    url(r'^dashboard/([A-Za-z0-9_]+)', login_required(dashboard),name="dashboard_page"),
    url(r'^raise_alert/', raise_alert),
    url(r'^view_https_mode/', login_required(view_https_mode)),
    url(r'^view_system_info/', login_required(view_system_info)),
    url(r'^edit_https_mode/', login_required(edit_https_mode)),
    url(r'^reload_manifest/', login_required(reload_manifest)),
    url(r'^flag_node/', flag_node),
    #url(r'^set_file_owner_and_permissions/', set_file_owner_and_permissions),
    url(r'^internal_audit/', internal_audit),
    url(r'^change_admin_password/', login_required(change_admin_password),name="change_admin_password"),
    url(r'^access_shell/', login_required(shell_access),name="shell_access"),
    url(r'^view_email_settings/', login_required(view_email_settings)),
    url(r'^configure_email_settings/', login_required(configure_email_settings)),
    url(r'^reset_to_factory_defaults/', login_required(reset_to_factory_defaults)),
    url(r'^view_alerts/', login_required(view_alerts)),
    url(r'^view_hardware_logs/', login_required(view_hardware_logs)),
    url(r'^view_audit_trail/', login_required(view_audit_trail)),
    url(r'^configure_ntp_settings/', login_required(configure_ntp_settings)),
    url(r'^view_ntp_settings/', login_required(view_ntp_settings)),
    url(r'^view_cifs_shares/', login_required(view_cifs_shares)),
    url(r'^delete_ace/', login_required(delete_ace)),
    url(r'^add_aces/', login_required(add_aces)),
    url(r'^view_dir_ownership_permissions/', login_required(view_dir_ownership_permissions)),
    url(r'^create_dir/', login_required(create_dir)),
    url(r'^get_dir_listing/', login_required(get_dir_listing)),
    url(r'^delete_dir/', login_required(delete_dir)),
    url(r'^modify_dir_owner/', login_required(modify_dir_owner)),
    url(r'^dir_manager/', login_required(dir_manager)),
    url(r'^edit_aces/', login_required(edit_aces)),
    url(r'^view_services/', login_required(view_services)),
    url(r'^view_ssl_certificates/', login_required(view_ssl_certificates)),
    url(r'^upload_ssl_certificate/', login_required(upload_ssl_certificate)),
    url(r'^create_self_signed_ssl_certificate/', login_required(create_self_signed_ssl_certificate)),
    url(r'^delete_ssl_certificate/', login_required(delete_ssl_certificate)),
    url(r'^change_service_status/', login_required(change_service_status)),
    url(r'^view_interfaces/', login_required(view_interfaces)),
    url(r'^set_interface_state/', login_required(set_interface_state)),
    url(r'^edit_interface_address/', login_required(edit_interface_address)),
    url(r'^view_nic/', login_required(view_nic)),
    url(r'^view_hostname/', login_required(view_hostname)),
    url(r'^view_iscsi_targets/', login_required(view_targets)),
    url(r'^view_iscsi_target/', login_required(view_target)),
    url(r'^create_iscsi_target/', login_required(create_iscsi_target)),
    url(r'^delete_iscsi_target/', login_required(delete_iscsi_target)),
    url(r'^create_iscsi_lun/', login_required(create_iscsi_lun)),
    url(r'^delete_iscsi_lun/', login_required(delete_iscsi_lun)),
    url(r'^add_iscsi_user_authentication/', login_required(add_iscsi_user_authentication)),
    url(r'^add_iscsi_acl/', login_required(add_iscsi_acl)),
    url(r'^remove_iscsi_acl/', login_required(remove_iscsi_acl)),
    url(r'^remove_iscsi_user_authentication/', login_required(remove_iscsi_user_authentication)),
    url(r'^edit_hostname/', login_required(edit_hostname)),
    url(r'^view_dns_nameservers/', login_required(view_dns_nameservers)),
    url(r'^edit_dns_nameservers/', login_required(edit_dns_nameservers)),
    url(r'^view_bond/', login_required(view_bond)),
    url(r'^remove_vlan/', login_required(remove_vlan)),
    url(r'^create_vlan/', login_required(create_vlan)),
    url(r'^remove_bond/', login_required(remove_bond)),
    url(r'^create_bond/', login_required(create_bond)),
    url(r'^modify_group_membership/', login_required(modify_group_membership)),
    url(r'^edit_local_user_gid/', login_required(edit_local_user_gid)),
    url(r'^edit_local_user_group_membership/', login_required(edit_local_user_group_membership)),
    url(r'^view_local_user/', login_required(view_local_user)),
    url(r'^view_local_users/', login_required(view_local_users)),
    url(r'^create_local_group/', login_required(create_local_group)),
    url(r'^delete_local_group/', login_required(delete_local_group)),
    url(r'^view_local_group/', login_required(view_local_group)),
    url(r'^view_local_groups/', login_required(view_local_groups)),
    url(r'^create_local_user/', login_required(create_local_user)),
    url(r'^delete_local_user/', login_required(delete_local_user)),
    url(r'^change_local_user_password/', login_required(change_local_user_password)),
    url(r'^export_zfs_pool/', login_required(export_zfs_pool)),
    url(r'^create_remote_replication/', login_required(create_remote_replication)),
    url(r'^remove_remote_replication/', login_required(remove_remote_replication)),
    url(r'^modify_remote_replication/', login_required(modify_remote_replication)),
    url(r'^view_remote_replications/', login_required(view_remote_replications)),
    url(r'^import_zfs_pool/', login_required(import_zfs_pool)),
    url(r'^add_zfs_spares/', login_required(add_zfs_spares)),
    url(r'^remove_zfs_spare/', login_required(remove_zfs_spare)),
    url(r'^set_zfs_quota/', login_required(set_zfs_quota)),
    url(r'^remove_zfs_quota/', login_required(remove_zfs_quota)),
    url(r'^view_backup/', login_required(view_backup)),
    url(r'^view_zfs_snapshots/', login_required(view_zfs_snapshots)),
    url(r'^create_zfs_snapshot/', login_required(create_zfs_snapshot)),
    url(r'^import_all_zfs_pools/', login_required(import_all_zfs_pools)),
    url(r'^schedule_zfs_snapshot/', login_required(schedule_zfs_snapshot)),
    url(r'^view_zfs_snapshot_schedules/', login_required(view_zfs_snapshot_schedules)),
    url(r'^rename_zfs_snapshot/', login_required(rename_zfs_snapshot)),
    url(r'^delete_zfs_snapshot/', login_required(delete_zfs_snapshot)),
    url(r'^rollback_zfs_snapshot/', login_required(rollback_zfs_snapshot)),
    url(r'^view_zfs_pools/', login_required(view_zfs_pools)),
    url(r'^set_zfs_slog/', login_required(set_zfs_slog)),
    url(r'^set_zfs_l2arc/', login_required(set_zfs_l2arc)),
    url(r'^remove_zfs_slog/', login_required(remove_zfs_slog)),
    url(r'^remove_zfs_l2arc/', login_required(remove_zfs_l2arc)),
    url(r'^view_disks/', login_required(view_disks)),
    url(r'^identify_disk/', login_required(identify_disk)),
    url(r'^view_zfs_pool/', login_required(view_zfs_pool)),
    url(r'^create_zfs_pool/', login_required(create_zfs_pool)),
    url(r'^expand_zfs_pool/', login_required(expand_zfs_pool)),
    url(r'^delete_zfs_pool/', login_required(delete_zfs_pool)),
    url(r'^scrub_zfs_pool/', login_required(scrub_zfs_pool)),
    url(r'^view_zfs_dataset/', login_required(view_zfs_dataset)),
    url(r'^edit_zfs_dataset/', login_required(edit_zfs_dataset)),
    url(r'^delete_zfs_dataset/', login_required(delete_zfs_dataset)),
    url(r'^create_zfs_dataset/', login_required(create_zfs_dataset)),
    url(r'^create_zfs_zvol/', login_required(create_zfs_zvol)),
    url(r'^view_zfs_zvol/', login_required(view_zfs_zvol)),
    url(r'^create_nfs_share/', login_required(create_nfs_share)),
    url(r'^view_nfs_shares/', login_required(view_nfs_shares)),
    url(r'^edit_nfs_share/', login_required(edit_nfs_share)),
    url(r'^view_nfs_share/', login_required(view_nfs_share)),
    url(r'^delete_nfs_share/', login_required(delete_nfs_share)),
    url(r'^create_cifs_share/', login_required(create_cifs_share)),
    url(r'^view_cifs_share/', login_required(view_cifs_share)),
    url(r'^view_cifs_shares/', login_required(view_cifs_shares)),
    url(r'^edit_cifs_share/', login_required(edit_cifs_share)),
    url(r'^edit_auth_method/', login_required(edit_auth_method)),
    url(r'^delete_cifs_share/', login_required(delete_cifs_share)),
    url(r'^auth_server_settings/', login_required(samba_server_settings)),
    url(r'^save_samba_server_settings/', login_required(save_samba_server_settings)),
    url(r'^replace_disk/', login_required(replace_disk)),
    url(r'^edit_integral_view_log_level/', login_required(edit_integral_view_log_level)),
    url(r'^show/([A-Za-z0-9_]+)/([a-zA-Z0-9_\-\.]*)', login_required(show),name="show_page"),
    url(r'^refresh_alerts/([0-9_]*)', login_required(refresh_alerts)),
    url(r'^logout/', logout,name="logout"),
    url(r'^view_log/', login_required(view_log)),
    url(r'^download_log/', login_required(download_log)),
    #url(r'^download_hardware_logs/', login_required(download_hardware_logs)),
    url(r'^download_sys_info/', login_required(download_sys_info)),
    url(r'^upload_sys_info/', login_required(upload_sys_info)),
    url(r'^rotate_log_list/', login_required(rotate_log)),
    url(r'^rotate_log/([A-Za-z_]+)', login_required(rotate_log)),
    url(r'^view_rotated_log_list/([A-Za-z_]+)', login_required(view_rotated_log_list)),
    url(r'^view_rotated_log_file/([A-Za-z_]+)', login_required(view_rotated_log_file)),
    url(r'dir_contents/',login_required(dir_contents)),
    url(r'^view_scheduled_jobs/', login_required(view_scheduled_jobs)),
    url(r'^download_cron_log', login_required(download_cron_log)),
    url(r'^remove_cron_job', login_required(remove_cron_job)),
    url(r'^view_background_tasks/', login_required(view_background_tasks)),
    url(r'^remove_background_task/', login_required(remove_background_task)),
    url(r'^view_task_details/([0-9]*)', login_required(view_task_details)),
    url(r'^modify_dir_permissions', login_required(modify_dir_permissions)),
    url(r'^view_routes', login_required(view_route)),
    url(r'^create_route', login_required(create_route)),
    url(r'^edit_route', login_required(edit_route)),
    url(r'^delete_route', login_required(delete_route)),
    url(r'^configure_ftp', login_required(configure_ftp)),
    url(r'^create_ftp_user_dirs', login_required(create_ftp_user_dirs)),
    url(r'^view_ftp_configuration', login_required(view_ftp_configuration)),
    url(r'^reboot_or_shutdown',login_required(reboot_or_shutdown)), 
    url(r'^user_ssh_keys',login_required(user_ssh_keys)),
    url(r'^known_hosts_ssh_keys',login_required(known_hosts_ssh_keys)),
    url(r'^upload_ssh_user_key',login_required(upload_ssh_user_key)),
    url(r'^upload_ssh_host_key',login_required(upload_ssh_host_key)),
    url(r'^create_rsync_share',login_required(create_rsync_share)),
    url(r'^edit_rsync_share',login_required(edit_rsync_share)),
    url(r'^view_rsync_shares',login_required(view_rsync_shares)),
    url(r'^delete_rsync_share',login_required(delete_rsync_share)),
)

