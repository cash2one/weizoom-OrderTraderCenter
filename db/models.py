# coding: utf8
from eaglet.core.db import models

WORD2EXPORT_JOB_TYPE = {
	'all_orders': 1,
	'financial_audit_orders': 3
}


class ExportJob(models.Model):
	woid = models.IntegerField()
	type = models.IntegerField(default=0)
	status = models.BooleanField(default=False)  # 其实是表示是否完成的bool
	processed_count = models.IntegerField()  # 已处理数量
	count = models.IntegerField()  # 总数量
	is_download = models.BooleanField(default=False, verbose_name='是否下载')
	param = models.CharField(max_length=1024)
	file_path = models.CharField(max_length=256)
	update_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)
	created_at = models.DateTimeField(verbose_name='创建时间')

	class Meta(object):
		db_table = 'export_job'
