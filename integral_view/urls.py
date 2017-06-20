from django.conf.urls import patterns, include, url

from integral_view.views.monitoring import view_read_write_stats, api_get_status, view_remote_monitoring_servers, update_remote_monitoring_server, delete_remote_monitoring_server, view_remote_monitoring_server_status

from integral_view.views.scheduler_cron_management import view_background_tasks, view_task_details, delete_background_task

from integral_view.views.disk_management import view_disks, identify_disk, replace_disk

from integral_view.views.remote_replication_management import create_remote_replication, view_remote_replications, delete_remote_replication, update_remote_replication

from integral_view.views.ntp_management import update_ntp_settings, view_ntp_settings, sync_ntp

from integral_view.views.admin_auth import login, logout, update_admin_password, view_email_settings, update_email_settings, view_https_mode, update_https_mode, reboot_or_shutdown

from integral_view.views.pki_management import view_ssl_certificates, delete_ssl_certificate, create_self_signed_ssl_certificate, upload_ssl_certificate, view_known_hosts_ssh_keys, view_user_ssh_keys, upload_ssh_user_key, upload_ssh_host_key

from integral_view.views.common import view_dashboard, access_shell, view_backup, update_manifest, flag_node, view_system_info

from integral_view.views.log_management import download_log, rotate_log, view_rotated_log_list, view_rotated_log_file, download_sys_info, upload_sys_info, refresh_alerts, view_alerts, view_log

from integral_view.views.cifs_share_management import view_cifs_shares, create_cifs_share, view_samba_server_settings, update_samba_server_settings, view_cifs_share, update_cifs_share, delete_cifs_share, update_auth_method

from integral_view.views.folder_management import delete_ace, create_aces, update_aces, update_dir_permissions, create_dir, delete_dir, view_dir_manager, update_dir_owner, view_dir_listing, view_dir_ownership_permissions, view_dir_contents, update_sticky_bit

from integral_view.views.local_user_management import view_local_users, create_local_user, update_local_user_password, delete_local_user, view_local_user, view_local_groups, update_local_user_group_membership, view_local_group, create_local_group, delete_local_group, update_group_membership

from integral_view.views.nfs_share_management import view_nfs_shares, view_nfs_share, delete_nfs_share, create_nfs_share, update_nfs_share

from integral_view.views.zfs_management import view_zfs_pools, view_zfs_pool, view_zfs_dataset, update_zfs_dataset, delete_zfs_dataset, create_zfs_dataset, view_zfs_snapshots, create_zfs_snapshot, delete_zfs_snapshot, rename_zfs_snapshot, rollback_zfs_snapshot, create_zfs_pool, delete_zfs_pool, update_zfs_slog, delete_zfs_slog, scrub_zfs_pool, clear_zfs_pool, create_zfs_zvol, view_zfs_zvol, import_all_zfs_pools, create_zfs_spares, delete_zfs_spare, expand_zfs_pool, delete_zfs_quota, update_zfs_quota, export_zfs_pool, import_zfs_pool, schedule_zfs_snapshot, update_zfs_l2arc, delete_zfs_l2arc, view_zfs_snapshot_schedules, update_zfs_dataset_advanced_properties

from integral_view.views.networking_management import view_interfaces, view_interface, view_bond, update_interface_state, update_interface_address, create_bond, delete_bond, view_hostname, update_hostname, view_dns_nameservers, update_dns_nameservers, delete_vlan, create_vlan

from integral_view.views.services_management import view_services, update_service_status

from integral_view.views.ftp_management import update_ftp_configuration, view_ftp_configuration, create_ftp_user_dirs

from integral_view.views.stgt_iscsi_management import view_targets, view_target, create_iscsi_target, delete_iscsi_target, create_iscsi_user_authentication, delete_iscsi_user_authentication, create_iscsi_lun, delete_iscsi_lun, create_iscsi_acl, delete_iscsi_acl

from integral_view.views.rsync_share_management import create_rsync_share, update_rsync_share, view_rsync_shares, delete_rsync_share

from django.contrib.auth.decorators import login_required

from integral_view.views.system import update_system_date_time, reset_to_factory_defaults

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', admin.site.urls),

                       # From views/admin_auth.py
                       url(r'^login/', login),
                       url(r'^logout/', logout, name="logout"),
                       url(r'^$', login),
                       url(r'^update_admin_password/',
                           login_required(update_admin_password)),
                       url(r'^view_email_settings/',
                           login_required(view_email_settings)),
                       url(r'^update_email_settings/',
                           login_required(update_email_settings)),
                       url(r'^view_https_mode/', login_required(view_https_mode)),
                       url(r'^update_https_mode/',
                           login_required(update_https_mode)),
                       url(r'^reboot_or_shutdown',
                           login_required(reboot_or_shutdown)),

                       # From views/monitoring.py
                       url(r'^api_get_status/', api_get_status),
                       url(r'^view_remote_monitoring_servers/',
                           view_remote_monitoring_servers),
                       url(r'^update_remote_monitoring_server/',
                           update_remote_monitoring_server),
                       url(r'^delete_remote_monitoring_server/',
                           delete_remote_monitoring_server),
                       url(r'^view_remote_monitoring_server_status/',
                           view_remote_monitoring_server_status),


                       # From views/cifs_share_management.py
                       url(r'^view_cifs_shares/',
                           login_required(view_cifs_shares)),
                       url(r'^view_cifs_share/', login_required(view_cifs_share)),
                       url(r'^update_cifs_share/',
                           login_required(update_cifs_share)),
                       url(r'^delete_cifs_share/',
                           login_required(delete_cifs_share)),
                       url(r'^create_cifs_share/',
                           login_required(create_cifs_share)),
                       url(r'^view_samba_server_settings/',
                           login_required(view_samba_server_settings)),
                       url(r'^update_samba_server_settings/',
                           login_required(update_samba_server_settings)),
                       url(r'^update_auth_method/',
                           login_required(update_auth_method)),

                       # Form views/system.py
                       url(r'^update_system_date_time/',
                           login_required(update_system_date_time)),
                       url(r'^reset_to_factory_defaults/',
                           login_required(reset_to_factory_defaults)),


                       # From views/config.py
                       url(r'^view_system_info/',
                           login_required(view_system_info)),
                       url(r'^update_manifest/', login_required(update_manifest)),
                       url(r'^flag_node/', flag_node),
                       url(r'^view_backup/', login_required(view_backup)),
                       url(r'^view_dashboard/([A-Za-z0-9_]+)',
                           login_required(view_dashboard)),
                       url(r'^access_shell/', login_required(access_shell)),

                       # From views/folder_management.py
                       url(r'view_dir_contents/',
                           login_required(view_dir_contents)),
                       url(r'^create_aces/', login_required(create_aces)),
                       url(r'^update_aces/', login_required(update_aces)),
                       url(r'^delete_ace/', login_required(delete_ace)),
                       url(r'^create_dir/', login_required(create_dir)),
                       url(r'^delete_dir/', login_required(delete_dir)),
                       url(r'^view_dir_listing/',
                           login_required(view_dir_listing)),
                       url(r'^view_dir_manager/',
                           login_required(view_dir_manager)),
                       url(r'^view_dir_ownership_permissions/',
                           login_required(view_dir_ownership_permissions)),
                       url(r'^update_dir_owner/',
                           login_required(update_dir_owner)),
                       url(r'^update_dir_permissions',
                           login_required(update_dir_permissions)),
                       url(r'^update_sticky_bit/',
                           login_required(update_sticky_bit)),

                       # From views/ftp_management.py
                       url(r'^view_ftp_configuration',
                           login_required(view_ftp_configuration)),
                       url(r'^update_ftp_configuration',
                           login_required(update_ftp_configuration)),
                       url(r'^create_ftp_user_dirs',
                           login_required(create_ftp_user_dirs)),

                       # From views/local_user_management.py
                       url(r'^view_local_users/',
                           login_required(view_local_users)),
                       url(r'^view_local_groups/',
                           login_required(view_local_groups)),
                       url(r'^view_local_user/', login_required(view_local_user)),
                       url(r'^view_local_group/',
                           login_required(view_local_group)),
                       url(r'^update_local_user_group_membership/',
                           login_required(update_local_user_group_membership)),
                       url(r'^create_local_user/',
                           login_required(create_local_user)),
                       url(r'^delete_local_group/',
                           login_required(delete_local_group)),
                       url(r'^create_local_group/',
                           login_required(create_local_group)),
                       url(r'^delete_local_user/',
                           login_required(delete_local_user)),
                       url(r'^update_local_user_password/',
                           login_required(update_local_user_password)),
                       url(r'^update_group_membership/',
                           login_required(update_group_membership)),

                       # From views/log_management.py
                       url(r'^view_log/', login_required(view_log)),
                       url(r'^view_alerts/', login_required(view_alerts)),
                       url(r'^download_log/', login_required(download_log)),
                       url(r'^rotate_log/([A-Za-z_]+)',
                           login_required(rotate_log)),
                       url(r'^download_sys_info/',
                           login_required(download_sys_info)),
                       url(r'^upload_sys_info/', login_required(upload_sys_info)),
                       url(r'^view_rotated_log_list/([A-Za-z_]+)',
                           login_required(view_rotated_log_list)),
                       url(r'^view_rotated_log_file/([A-Za-z_]+)',
                           login_required(view_rotated_log_file)),
                       url(r'^refresh_alerts/([0-9_]*)',
                           login_required(refresh_alerts)),

                       # From views/networking_management.py
                       url(r'^view_interfaces/', login_required(view_interfaces)),
                       url(r'^view_interface/', login_required(view_interface)),
                       url(r'^update_interface_state/',
                           login_required(update_interface_state)),
                       url(r'^view_bond/', login_required(view_bond)),
                       url(r'^update_interface_address/',
                           login_required(update_interface_address)),
                       url(r'^create_vlan/', login_required(create_vlan)),
                       url(r'^delete_vlan/', login_required(delete_vlan)),
                       url(r'^create_bond/', login_required(create_bond)),
                       url(r'^delete_bond/', login_required(delete_bond)),
                       url(r'^view_hostname/', login_required(view_hostname)),
                       url(r'^update_hostname/', login_required(update_hostname)),
                       url(r'^view_dns_nameservers/',
                           login_required(view_dns_nameservers)),
                       url(r'^update_dns_nameservers/',
                           login_required(update_dns_nameservers)),

                       # From views/nfs_share_management.py
                       url(r'^view_nfs_shares/', login_required(view_nfs_shares)),
                       url(r'^view_nfs_share/', login_required(view_nfs_share)),
                       url(r'^delete_nfs_share/',
                           login_required(delete_nfs_share)),
                       url(r'^update_nfs_share/',
                           login_required(update_nfs_share)),
                       url(r'^create_nfs_share/',
                           login_required(create_nfs_share)),

                       # From views/ntp_management.py
                       url(r'^view_ntp_settings/',
                           login_required(view_ntp_settings)),
                       url(r'^update_ntp_settings/',
                           login_required(update_ntp_settings)),
                       url(r'^sync_ntp/',
                           login_required(sync_ntp)),

                       # From views/pki_management.py
                       url(r'^view_ssl_certificates/',
                           login_required(view_ssl_certificates)),
                       url(r'^delete_ssl_certificate/',
                           login_required(delete_ssl_certificate)),
                       url(r'^create_self_signed_ssl_certificate/',
                           login_required(create_self_signed_ssl_certificate)),
                       url(r'^upload_ssl_certificate/',
                           login_required(upload_ssl_certificate)),
                       url(r'^upload_ssh_user_key',
                           login_required(upload_ssh_user_key)),
                       url(r'^upload_ssh_host_key',
                           login_required(upload_ssh_host_key)),
                       url(r'^view_user_ssh_keys',
                           login_required(view_user_ssh_keys)),
                       url(r'^view_known_hosts_ssh_keys',
                           login_required(view_known_hosts_ssh_keys)),

                       # From views/rsync_share_management.py
                       url(r'^create_rsync_share',
                           login_required(create_rsync_share)),
                       url(r'^update_rsync_share',
                           login_required(update_rsync_share)),
                       url(r'^view_rsync_shares',
                           login_required(view_rsync_shares)),
                       url(r'^delete_rsync_share',
                           login_required(delete_rsync_share)),

                       # From views/scheduler_cron_management.py
                       url(r'^view_background_tasks/',
                           login_required(view_background_tasks)),
                       url(r'^delete_background_task/',
                           login_required(delete_background_task)),
                       url(r'^view_task_details/([0-9]*)',
                           login_required(view_task_details)),

                       # From views/services_management.py
                       url(r'^view_services/', login_required(view_services)),
                       url(r'^update_service_status/',
                           login_required(update_service_status)),

                       # From views/stgt_iscsi_management.py
                       url(r'^view_iscsi_targets/',
                           login_required(view_targets)),
                       url(r'^view_iscsi_target/', login_required(view_target)),
                       url(r'^create_iscsi_target/',
                           login_required(create_iscsi_target)),
                       url(r'^delete_iscsi_target/',
                           login_required(delete_iscsi_target)),
                       url(r'^create_iscsi_lun/',
                           login_required(create_iscsi_lun)),
                       url(r'^delete_iscsi_lun/',
                           login_required(delete_iscsi_lun)),
                       url(r'^create_iscsi_user_authentication/',
                           login_required(create_iscsi_user_authentication)),
                       url(r'^delete_iscsi_user_authentication/',
                           login_required(delete_iscsi_user_authentication)),
                       url(r'^create_iscsi_acl/',
                           login_required(create_iscsi_acl)),
                       url(r'^delete_iscsi_acl/',
                           login_required(delete_iscsi_acl)),

                       # From views/disk_management.py
                       url(r'^view_disks/', login_required(view_disks)),
                       url(r'^identify_disk/', login_required(identify_disk)),
                       url(r'^replace_disk/', login_required(replace_disk)),

                       # From views/remote_replication_management.py
                       url(r'^view_remote_replications/',
                           login_required(view_remote_replications)),
                       url(r'^create_remote_replication/',
                           login_required(create_remote_replication)),
                       url(r'^update_remote_replication/',
                           login_required(update_remote_replication)),
                       url(r'^delete_remote_replication/',
                           login_required(delete_remote_replication)),

                       # From views/zfs_management.py
                       url(r'^view_zfs_pools/', login_required(view_zfs_pools)),
                       url(r'^view_zfs_pool/', login_required(view_zfs_pool)),
                       url(r'^update_zfs_quota/',
                           login_required(update_zfs_quota)),
                       url(r'^delete_zfs_quota/',
                           login_required(delete_zfs_quota)),
                       url(r'^export_zfs_pool/', login_required(export_zfs_pool)),
                       url(r'^import_all_zfs_pools/',
                           login_required(import_all_zfs_pools)),
                       url(r'^import_zfs_pool/', login_required(import_zfs_pool)),
                       url(r'^create_zfs_pool/', login_required(create_zfs_pool)),
                       url(r'^expand_zfs_pool/', login_required(expand_zfs_pool)),
                       url(r'^scrub_zfs_pool/', login_required(scrub_zfs_pool)),
                       url(r'^clear_zfs_pool/', login_required(clear_zfs_pool)),
                       url(r'^delete_zfs_pool/', login_required(delete_zfs_pool)),
                       url(r'^update_zfs_slog/', login_required(update_zfs_slog)),
                       url(r'^delete_zfs_slog/', login_required(delete_zfs_slog)),
                       url(r'^update_zfs_l2arc/',
                           login_required(update_zfs_l2arc)),
                       url(r'^delete_zfs_l2arc/',
                           login_required(delete_zfs_l2arc)),
                       url(r'^view_zfs_dataset/',
                           login_required(view_zfs_dataset)),
                       url(r'^update_zfs_dataset/',
                           login_required(update_zfs_dataset)),
                       url(r'^update_zfs_dataset_advanced_properties/',
                           login_required(update_zfs_dataset_advanced_properties)),
                       url(r'^delete_zfs_dataset/',
                           login_required(delete_zfs_dataset)),
                       url(r'^create_zfs_dataset/',
                           login_required(create_zfs_dataset)),
                       url(r'^create_zfs_zvol/', login_required(create_zfs_zvol)),
                       url(r'^view_zfs_zvol/', login_required(view_zfs_zvol)),
                       url(r'^view_zfs_snapshots/',
                           login_required(view_zfs_snapshots)),
                       url(r'^create_zfs_snapshot/',
                           login_required(create_zfs_snapshot)),
                       url(r'^delete_zfs_snapshot/',
                           login_required(delete_zfs_snapshot)),
                       url(r'^rollback_zfs_snapshot/',
                           login_required(rollback_zfs_snapshot)),
                       url(r'^rename_zfs_snapshot/',
                           login_required(rename_zfs_snapshot)),
                       url(r'^view_zfs_snapshot_schedules/',
                           login_required(view_zfs_snapshot_schedules)),
                       url(r'^schedule_zfs_snapshot/',
                           login_required(schedule_zfs_snapshot)),
                       url(r'^create_zfs_spares/',
                           login_required(create_zfs_spares)),
                       url(r'^delete_zfs_spare/',
                           login_required(delete_zfs_spare)),
                       )


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
