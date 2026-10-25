-- ============================================================
-- 课程表重构建表脚本（手动执行）
-- 在 school_db 库下执行本脚本
-- 注意：脚本会先 DROP 旧 subject 表，旧数据将被清除（由初始数据替代）
-- ============================================================

DROP TABLE IF EXISTS `subject`;

CREATE TABLE `subject` (
    `id`          INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID，自增整型',
    `name`        VARCHAR(50)  NOT NULL COMMENT '课程名称',
    `credit`      INT          NOT NULL DEFAULT 0 COMMENT '学分，默认为 0',
    `teacher_id`  INT          NOT NULL COMMENT '授课教师id，外键关联教师表',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（默认当前时间戳）',
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_subject_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- ============================================================
-- 初始数据（手动执行；teacher_id 请使用 teacher 表中已存在的教师id）
-- create_time 不传，由数据库默认填充当前时间
-- 注意：重复执行本段会重复插入
-- ============================================================

INSERT INTO `subject` (`name`, `credit`, `teacher_id`) VALUES
('高等数学', 4, 1),
('大学英语', 3, 2),
('大学物理', 4, 3),
('数据结构', 5, 1);

-- 学分不传，演示数据库默认值 0
INSERT INTO `subject` (`name`, `teacher_id`) VALUES
('体育', 2);
