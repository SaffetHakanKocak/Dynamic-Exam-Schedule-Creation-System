/* =========  A) FRESH INSTALL  ========= */
DROP DATABASE IF EXISTS exam_scheduler;
CREATE DATABASE exam_scheduler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE exam_scheduler;

/* ——— Temel ——— */
CREATE TABLE departments (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE users (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  email          VARCHAR(120) NOT NULL UNIQUE,
  password_hash  VARCHAR(200) NOT NULL,
  role           ENUM('ADMIN','COORD') NOT NULL,
  department_id  INT NULL,
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_users_dept FOREIGN KEY (department_id) REFERENCES departments(id)
) ENGINE=InnoDB;

/* ——— Derslik ——— */
CREATE TABLE classrooms (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  department_id  INT NOT NULL,
  code           VARCHAR(32) NOT NULL,
  name           VARCHAR(100) NOT NULL,
  seat_group     TINYINT NOT NULL,
  num_rows       INT NOT NULL,
  num_cols       INT NOT NULL,
  capacity       INT AS (num_rows * num_cols * seat_group) STORED NOT NULL,
  UNIQUE KEY uq_room_code (department_id, code),
  KEY idx_rooms_dept (department_id),
  CONSTRAINT fk_rooms_dept FOREIGN KEY (department_id) REFERENCES departments(id),
  CONSTRAINT chk_rooms_seatgroup CHECK (seat_group IN (2,3)),
  CONSTRAINT chk_rooms_pos CHECK (num_rows > 0 AND num_cols > 0)
) ENGINE=InnoDB;

/* ——— Akademik ——— */
CREATE TABLE instructors (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(160) NOT NULL,
  UNIQUE KEY uq_instructor_name (name)
) ENGINE=InnoDB;

CREATE TABLE courses (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  department_id INT NOT NULL,
  code          VARCHAR(32) NOT NULL,
  name          VARCHAR(200) NOT NULL,
  instructor_id INT NULL,
  grade_level   TINYINT NULL,
  is_elective   TINYINT(1) DEFAULT 0,
  UNIQUE KEY uq_course_dept_code (department_id, code),
  KEY idx_course_instructor (instructor_id),
  KEY idx_courses_dept (department_id),
  CONSTRAINT fk_course_dept       FOREIGN KEY (department_id) REFERENCES departments(id),
  CONSTRAINT fk_course_instructor FOREIGN KEY (instructor_id)  REFERENCES instructors(id)
) ENGINE=InnoDB;

CREATE TABLE students (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  number        VARCHAR(32) NOT NULL,
  name          VARCHAR(160) NOT NULL,
  grade_level   TINYINT NULL,
  department_id INT NOT NULL,
  UNIQUE KEY uq_student_number (number),
  KEY idx_students_dept (department_id),
  CONSTRAINT fk_students_dept FOREIGN KEY (department_id) REFERENCES departments(id)
) ENGINE=InnoDB;

CREATE TABLE enrollments (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  course_id  INT NOT NULL,
  UNIQUE KEY uq_enrollment (student_id, course_id),
  KEY idx_enr_student (student_id),
  KEY idx_enr_course (course_id),
  CONSTRAINT fk_enr_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT fk_enr_course  FOREIGN KEY (course_id)  REFERENCES courses(id)  ON DELETE CASCADE
) ENGINE=InnoDB;

/* ——— Planlama ——— */
CREATE TABLE exam_terms (
  id                   INT AUTO_INCREMENT PRIMARY KEY,
  name                 ENUM('VIZE','FINAL','BUT') NOT NULL,
  date_start           DATE NOT NULL,
  date_end             DATE NOT NULL,
  days_off             SET('MON','TUE','WED','THU','FRI','SAT','SUN') DEFAULT 'SAT,SUN',
  default_duration_min INT NOT NULL DEFAULT 75,
  min_gap_min          INT NOT NULL DEFAULT 15,
  CONSTRAINT chk_term_dates CHECK (date_start <= date_end)
) ENGINE=InnoDB;

CREATE TABLE timeslots (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  exam_term_id INT NOT NULL,
  starts_at    DATETIME NOT NULL,
  ends_at      DATETIME NOT NULL,
  UNIQUE KEY uq_timeslot_starts (exam_term_id, starts_at),
  KEY idx_timeslots_term (exam_term_id),
  CONSTRAINT fk_timeslot_term FOREIGN KEY (exam_term_id) REFERENCES exam_terms(id),
  CONSTRAINT chk_timeslot_range CHECK (starts_at < ends_at)
) ENGINE=InnoDB;

CREATE TABLE exams (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  course_id    INT NOT NULL,
  exam_term_id INT NOT NULL,
  timeslot_id  INT NULL,
  status       ENUM('PLANNED','ERROR','CONFIRMED') DEFAULT 'PLANNED',
  UNIQUE KEY uq_exam_unique (course_id, exam_term_id),
  KEY idx_exams_term (exam_term_id),
  KEY idx_exams_timeslot (timeslot_id),
  CONSTRAINT fk_exam_course FOREIGN KEY (course_id)    REFERENCES courses(id),
  CONSTRAINT fk_exam_term   FOREIGN KEY (exam_term_id) REFERENCES exam_terms(id),
  CONSTRAINT fk_exam_slot   FOREIGN KEY (timeslot_id)  REFERENCES timeslots(id) ON DELETE SET NULL
) ENGINE=InnoDB;

/* ——— Salon Atamaları ——— */
CREATE TABLE exam_rooms (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  exam_id      INT NOT NULL,
  classroom_id INT NOT NULL,
  timeslot_id  INT NOT NULL,
  UNIQUE KEY uq_room_timeslot (classroom_id, timeslot_id),
  UNIQUE KEY uq_exam_room (exam_id, classroom_id),
  KEY idx_examrooms_exam (exam_id),
  KEY idx_examrooms_classroom (classroom_id),
  KEY idx_examrooms_timeslot (timeslot_id),
  CONSTRAINT fk_examroom_exam FOREIGN KEY (exam_id)      REFERENCES exams(id)       ON DELETE CASCADE,
  CONSTRAINT fk_examroom_room FOREIGN KEY (classroom_id) REFERENCES classrooms(id)  ON DELETE RESTRICT,
  CONSTRAINT fk_examroom_slot FOREIGN KEY (timeslot_id)  REFERENCES timeslots(id)   ON DELETE RESTRICT
) ENGINE=InnoDB;

/* ——— Koltuk Atamaları ——— */
CREATE TABLE exam_seats (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  exam_id      INT NOT NULL,
  exam_room_id INT NOT NULL,
  student_id   INT NOT NULL,
  seat_row     INT NOT NULL,
  seat_col     INT NOT NULL,
  UNIQUE KEY uq_room_seat    (exam_room_id, seat_row, seat_col),
  UNIQUE KEY uq_exam_student (exam_id, student_id),
  KEY idx_seats_exam (exam_id),
  KEY idx_seats_room (exam_room_id),
  KEY idx_seats_student (student_id),
  CONSTRAINT fk_seat_exam    FOREIGN KEY (exam_id)      REFERENCES exams(id)      ON DELETE CASCADE,
  CONSTRAINT fk_seat_room    FOREIGN KEY (exam_room_id) REFERENCES exam_rooms(id) ON DELETE CASCADE,
  CONSTRAINT fk_seat_student FOREIGN KEY (student_id)   REFERENCES students(id)   ON DELETE CASCADE,
  CONSTRAINT chk_seat_pos CHECK (seat_row > 0 AND seat_col > 0)
) ENGINE=InnoDB;

/* ——— Süre İstisnaları ——— */
CREATE TABLE exam_exceptions (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  course_id    INT NOT NULL,
  exam_term_id INT NOT NULL,
  duration_min INT NOT NULL,
  UNIQUE KEY uq_exception (course_id, exam_term_id),
  CONSTRAINT fk_xc_course FOREIGN KEY (course_id)    REFERENCES courses(id)    ON DELETE CASCADE,
  CONSTRAINT fk_xc_term   FOREIGN KEY (exam_term_id) REFERENCES exam_terms(id) ON DELETE CASCADE,
  CONSTRAINT chk_xc_duration CHECK (duration_min > 0)
) ENGINE=InnoDB;

/* ——— Tutarlılık Trigger’ları ——— */
DELIMITER $$

CREATE TRIGGER trg_exam_rooms_bi
BEFORE INSERT ON exam_rooms
FOR EACH ROW
BEGIN
  DECLARE exam_slot INT;
  SELECT timeslot_id INTO exam_slot FROM exams WHERE id = NEW.exam_id;
  IF exam_slot IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exam has no timeslot; cannot assign room.';
  END IF;
  IF NEW.timeslot_id <> exam_slot THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'exam_rooms.timeslot_id must match exams.timeslot_id.';
  END IF;
END$$

CREATE TRIGGER trg_exam_rooms_bu
BEFORE UPDATE ON exam_rooms
FOR EACH ROW
BEGIN
  DECLARE exam_slot INT;
  SELECT timeslot_id INTO exam_slot FROM exams WHERE id = NEW.exam_id;
  IF exam_slot IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exam has no timeslot; cannot assign room.';
  END IF;
  IF NEW.timeslot_id <> exam_slot THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'exam_rooms.timeslot_id must match exams.timeslot_id.';
  END IF;
END$$

DELIMITER ;

/* ——— Seed ——— */
INSERT INTO departments (id, name) VALUES
(1,'Bilgisayar Mühendisliği'),
(2,'Yazılım Mühendisliği'),
(3,'Elektrik Mühendisliği'),
(4,'Elektronik Mühendisliği'),
(5,'İnşaat Mühendisliği');

/* Varsayılan admin — Şifre: Admin#1234
   Hash byte‐tamlık için HEX literal ile yazıldı (X'...'). */
DELETE FROM users WHERE TRIM(LOWER(email))='admin@example.com';

INSERT INTO users (email, password_hash, role, department_id)
VALUES (
  'admin@example.com',
  '$2b$12$C1UL2zXU1qS3OcHK3U6DFOX3b0cxi8HdpmbjYiqcEb1fW9.rHF8h6',  -- Admin#1234timeslotsusers
  'ADMIN',
  NULL
);

UPDATE users
SET password_hash = '$2b$12$AxlbmMtPMQYre.zezMMkIeAXx9Mc6mdih/2fLYoHWdkVn9fEZIP5u'
WHERE TRIM(LOWER(email)) = 'admin@example.com';


/* Örnek koordinatör eklemek istersen:
INSERT INTO users (email, password_hash, role, department_id)
VALUES ('coord.bm@example.com',
        X'2432622431322452615474622f437263353067797736554e4b554866754c4d6f72434847366f7538535a3148624659754f4279795863486d6364422e', -- şifre: 123
        'COORD', 1);
*/
