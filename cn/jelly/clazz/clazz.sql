-- ============================================================
-- 班级表建表脚本（手动执行）
-- 在 school_db 库下执行本脚本
-- ============================================================

CREATE TABLE IF NOT EXISTS `clazz` (
    `id`          INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID，自增整型',
    `name`        VARCHAR(50)  NOT NULL COMMENT '班级名称',
    `code`        VARCHAR(50)  NOT NULL COMMENT '班级编号',
    `teacher_id`  INT UNSIGNED NOT NULL COMMENT '班主任教师id',
    `address`     VARCHAR(100) DEFAULT NULL COMMENT '班级地址',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（默认当前时间戳）',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级表';

-- ============================================================
-- 测试数据（手动执行；teacher_id 请使用 teacher 表中已存在的教师id）
-- create_time 不传，由数据库默认填充当前时间
-- 注意：本段重复执行会重复插入，如需重跑请先 TRUNCATE TABLE clazz;
-- ============================================================

INSERT INTO `clazz` (`name`, `code`, `teacher_id`, `address`) VALUES
('高一（1）班', 'GZ-2026-01', 1, '教学楼A-101'),
('高一（2）班', 'GZ-2026-02', 2, '教学楼A-102'),
('高二（1）班', 'GZ-2026-03', 3, '教学楼B-201'),
('高二（3）班', 'GZ-2026-04', 1, '教学楼B-203'),
('高三（2）班', 'GZ-2026-05', 2, '教学楼C-301'),
('高三（5）班', 'GZ-2026-06', 3, NULL);
