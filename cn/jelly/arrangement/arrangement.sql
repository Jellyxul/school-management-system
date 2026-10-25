-- ============================================================
-- 排课表建表脚本（手动执行）
-- 在 school_db 库下执行本脚本
-- 依赖：subject、teacher 表需已存在
-- 说明：course_id 与 subject.id 同为 INT UNSIGNED，teacher_id 与 teacher.id 同为 INT，
--       类型一致才能建立外键
-- ============================================================

DROP TABLE IF EXISTS `arrangement`;

CREATE TABLE `arrangement` (
    `id`          INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID，自增整型',
    `course_id`   INT UNSIGNED NOT NULL COMMENT '课程id，外键关联课程表',
    `teacher_id`  INT          NOT NULL COMMENT '教师id，外键关联教师表',
    `term`        VARCHAR(20)  NOT NULL COMMENT '学期，如 2026-2027-1（不传时由服务端默认当前学期）',
    `classroom`   VARCHAR(50)  NOT NULL COMMENT '上课教室',
    `class_time`  VARCHAR(50)  NOT NULL COMMENT '上课时间，如 周一 1-2节',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（默认当前时间戳）',
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_arrangement_course` FOREIGN KEY (`course_id`) REFERENCES `subject` (`id`),
    CONSTRAINT `fk_arrangement_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='排课表';

-- ============================================================
-- 初始数据（手动执行；course_id 对应 subject 初始数据 1~5，teacher_id 使用 1~3）
-- create_time 不传，由数据库默认填充当前时间
-- 注意：重复执行本段会重复插入
-- ============================================================

INSERT INTO `arrangement` (`course_id`, `teacher_id`, `term`, `classroom`, `class_time`) VALUES
(1, 1, '2026-2027-1', '教学楼A-101', '周一 1-2节'),
(2, 2, '2026-2027-1', '教学楼A-102', '周二 3-4节'),
(3, 3, '2026-2027-1', '教学楼B-201', '周三 1-2节'),
(4, 1, '2026-2027-1', '教学楼B-202', '周四 3-4节'),
(5, 2, '2026-2027-1', '操场', '周五 5-6节');
