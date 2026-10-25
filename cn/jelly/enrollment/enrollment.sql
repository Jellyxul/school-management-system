-- ============================================================
-- 选课与成绩表建表脚本（手动执行）
-- 在 school_db 库下执行本脚本
-- 依赖：student、subject 表需已存在
-- 说明：course_id 与 subject.id 同为 INT UNSIGNED，student_id 与 student.id 同为 INT，
--       类型一致才能建立外键
-- ============================================================

DROP TABLE IF EXISTS `enrollment`;

CREATE TABLE `enrollment` (
    `id`          INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID，自增整型',
    `student_id`  INT          NOT NULL COMMENT '学生id，外键关联学生表',
    `course_id`   INT UNSIGNED NOT NULL COMMENT '课程id，外键关联课程表',
    `term`        VARCHAR(20)  NOT NULL COMMENT '学期，如 2026-2027-1（不传时由服务端默认当前学期）',
    `score`       INT          DEFAULT NULL COMMENT '成绩，默认为空（未录入）',
    `status`      VARCHAR(10)  NOT NULL DEFAULT '已选' COMMENT '状态，默认已选',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（默认当前时间戳）',
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_enrollment_student` FOREIGN KEY (`student_id`) REFERENCES `student` (`id`),
    CONSTRAINT `fk_enrollment_course` FOREIGN KEY (`course_id`) REFERENCES `subject` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选课与成绩表';

-- ============================================================
-- 初始数据（手动执行；student_id 使用学生表已存在的 id，course_id 对应 subject 初始数据 1~5）
-- score 不传即为 NULL（未录入）；status 不传默认"已选"；create_time 由数据库默认填充
-- 注意：重复执行本段会重复插入
-- ============================================================

INSERT INTO `enrollment` (`student_id`, `course_id`, `term`, `score`) VALUES
(1, 1, '2026-2027-1', 88),
(2, 1, '2026-2027-1', 92),
(3, 2, '2026-2027-1', 76),
(4, 3, '2026-2027-1', NULL),
(5, 4, '2026-2027-1', NULL),
(6, 5, '2026-2027-1', 85);

-- 演示：status/score 均不传，使用默认值（已选 / NULL）
INSERT INTO `enrollment` (`student_id`, `course_id`, `term`) VALUES
(7, 2, '2026-2027-1');
