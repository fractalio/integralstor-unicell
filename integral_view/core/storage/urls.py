from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.storage.views.disk_management import view_disks, identify_disk, replace_disk

from integral_view.core.storage.views.folder_management import delete_ace, create_aces, update_aces, update_dir_permissions, create_dir, delete_dir, view_dir_manager, update_dir_owner, view_dir_listing, view_dir_ownership_permissions, view_dir_contents, update_sticky_bit

from integral_view.core.storage.views.zfs_management import view_zfs_pools, view_zfs_pool, view_zfs_dataset, update_zfs_dataset, delete_zfs_dataset, create_zfs_dataset, view_zfs_snapshots, create_zfs_snapshot, delete_zfs_snapshot, delete_all_zfs_snapshots, rename_zfs_snapshot, rollback_zfs_snapshot, create_zfs_pool, delete_zfs_pool, update_zfs_slog, delete_zfs_slog, scrub_zfs_pool, clear_zfs_pool, create_zfs_zvol, view_zfs_zvol, import_all_zfs_pools, create_zfs_spares, delete_zfs_spare, expand_zfs_pool, delete_zfs_quota, update_zfs_quota, export_zfs_pool, import_zfs_pool, schedule_zfs_snapshot, update_zfs_l2arc, delete_zfs_l2arc, view_zfs_snapshot_schedules, update_zfs_dataset_advanced_properties, api_get_pool_usage_stats, view_zfs_historical_usage, view_zfs_pool_history_events, create_zfs_pool_scrub_schedule, delete_zfs_pool_scrub_schedule

urlpatterns = patterns('',
                       # From views/disk_management.py
                       url(r'^view_disks/', login_required(view_disks)),
                       url(r'^identify_disk/', login_required(identify_disk)),
                       url(r'^replace_disk/', login_required(replace_disk)),

                       url(r'^$', login_required(view_disks)),

                       # From views/zfs_management.py
                       url(r'^api_get_pool_usage_stats/',
                           api_get_pool_usage_stats),
                       url(r'^view_zfs_historical_usage/',
                           login_required(view_zfs_historical_usage)),
                       url(r'^view_zfs_pools/', login_required(view_zfs_pools)),
                       url(r'^view_zfs_pool/', login_required(view_zfs_pool)),
                       url(r'^view_zfs_pool_history_events/', login_required(view_zfs_pool_history_events)),
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
                       url(r'^create_zfs_pool_scrub_schedule/', login_required(create_zfs_pool_scrub_schedule)),
                       url(r'^delete_zfs_pool_scrub_schedule/', login_required(delete_zfs_pool_scrub_schedule)),
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
                       url(r'^delete_all_zfs_snapshots/',
                           login_required(delete_all_zfs_snapshots)),
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
                        )
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
