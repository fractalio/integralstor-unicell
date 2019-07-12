from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.storage_access.views.cifs_share_management import view_cifs_shares, create_cifs_share, view_samba_server_settings, update_samba_server_settings, view_cifs_share, update_cifs_share, delete_cifs_share, update_auth_method
from integral_view.core.storage_access.views.nfs_share_management import view_nfs_shares, view_nfs_share, delete_nfs_share, create_nfs_share, update_nfs_share
from integral_view.core.storage_access.views.afp_volume_management import view_afp_volumes, rename_afp_volume, delete_afp_volume, create_afp_volume
from integral_view.core.storage_access.views.ftp_management import update_ftp_configuration, view_ftp_configuration, create_ftp_user_dirs
from integral_view.core.storage_access.views.stgt_iscsi_management import view_targets, view_target, create_iscsi_target, delete_iscsi_target, create_iscsi_user_authentication, delete_iscsi_user_authentication, create_iscsi_lun, delete_iscsi_lun, create_iscsi_acl, delete_iscsi_acl
from integral_view.core.storage_access.views.rsync_share_management import create_rsync_share, update_rsync_share, view_rsync_shares, delete_rsync_share


urlpatterns = [
                       url(r'^$', login_required(view_nfs_shares)),
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

                       # From views/ftp_management.py
                       url(r'^view_ftp_configuration',
                           login_required(view_ftp_configuration)),
                       url(r'^update_ftp_configuration',
                           login_required(update_ftp_configuration)),
                       url(r'^create_ftp_user_dirs',
                           login_required(create_ftp_user_dirs)),

                       # From views/nfs_share_management.py
                       url(r'^view_nfs_shares/', login_required(view_nfs_shares)),
                       url(r'^view_nfs_share/', login_required(view_nfs_share)),
                       url(r'^delete_nfs_share/',
                           login_required(delete_nfs_share)),
                       url(r'^update_nfs_share/',
                           login_required(update_nfs_share)),
                       url(r'^create_nfs_share/',
                           login_required(create_nfs_share)),

                       # From views/afp_volume__management.py
                       url(r'^view_afp_volumes/', login_required(view_afp_volumes)),
                       url(r'^rename_afp_volume/', login_required(rename_afp_volume)),
                       url(r'^delete_afp_volume/', login_required(delete_afp_volume)),
                       url(r'^create_afp_volume/', login_required(create_afp_volume)),

                       # From views/rsync_share_management.py
                       url(r'^create_rsync_share',
                           login_required(create_rsync_share)),
                       url(r'^update_rsync_share',
                           login_required(update_rsync_share)),
                       url(r'^view_rsync_shares',
                           login_required(view_rsync_shares)),
                       url(r'^delete_rsync_share',
                           login_required(delete_rsync_share)),

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
]

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
