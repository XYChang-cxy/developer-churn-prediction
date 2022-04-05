/*
 Navicat MySQL Data Transfer

 Source Server         : LocalDBs
 Source Server Type    : MySQL
 Source Server Version : 80025
 Source Host           : localhost:3306
 Source Schema         : churn_database

 Target Server Type    : MySQL
 Target Server Version : 80025
 File Encoding         : 65001

 Date: 01/04/2022 15:26:54
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for churn_awesome_production_repos
-- ----------------------------
DROP TABLE IF EXISTS `churn_awesome_production_repos`;
CREATE TABLE `churn_awesome_production_repos`  (
  `repo_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `repo_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `repo_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_production_types` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `main_language` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `languages` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `star_count` int NULL DEFAULT NULL,
  `watch_count` int NULL DEFAULT NULL,
  `fork_count` int NULL DEFAULT NULL,
  `open_issue_pull_count` int NULL DEFAULT NULL,
  `open_issue_count` int NULL DEFAULT NULL,
  `open_pull_count` int NULL DEFAULT NULL,
  `issue_count` int NULL DEFAULT NULL,
  `pull_count` int NULL DEFAULT NULL,
  `commit_count` int NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `lifespan_day` int NULL DEFAULT NULL,
  PRIMARY KEY (`repo_name`, `platform`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for churn_awesome_repos
-- ----------------------------
DROP TABLE IF EXISTS `churn_awesome_repos`;
CREATE TABLE `churn_awesome_repos`  (
  `repo_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `repo_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `repo_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_language_labels` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_type` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_repo_types` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `main_language` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `languages` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `star_count` int NULL DEFAULT NULL,
  `watch_count` int NULL DEFAULT NULL,
  `fork_count` int NULL DEFAULT NULL,
  `open_issue_pull_count` int NULL DEFAULT NULL,
  `open_issue_count` int NULL DEFAULT NULL,
  `open_pull_count` int NULL DEFAULT NULL,
  `issue_count` int NULL DEFAULT NULL,
  `pull_count` int NULL DEFAULT NULL,
  `commit_count` int NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `lifespan_day` int NULL DEFAULT NULL,
  PRIMARY KEY (`repo_name`, `platform`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for churn_famous_repos
-- ----------------------------
DROP TABLE IF EXISTS `churn_famous_repos`;
CREATE TABLE `churn_famous_repos`  (
  `repo_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `repo_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `repo_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `main_language` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `languages` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `star_count` int NULL DEFAULT NULL,
  `watch_count` int NULL DEFAULT NULL,
  `fork_count` int NULL DEFAULT NULL,
  `open_issue_pull_count` int NULL DEFAULT NULL,
  `open_issue_count` int NULL DEFAULT NULL,
  `open_pull_count` int NULL DEFAULT NULL,
  `issue_count` int NULL DEFAULT NULL,
  `pull_count` int NULL DEFAULT NULL,
  `commit_count` int NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `lifespan_day` int NULL DEFAULT NULL,
  `is_awesome` binary(1) NULL DEFAULT NULL,
  PRIMARY KEY (`repo_name`, `platform`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for churn_search_repos
-- ----------------------------
DROP TABLE IF EXISTS `churn_search_repos`;
CREATE TABLE `churn_search_repos`  (
  `repo_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `repo_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `repo_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `main_language` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `languages` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `star_count` int NULL DEFAULT NULL,
  `watch_count` int NULL DEFAULT NULL,
  `fork_count` int NULL DEFAULT NULL,
  `open_issue_pull_count` int NULL DEFAULT NULL,
  `open_issue_count` int NULL DEFAULT NULL,
  `open_pull_count` int NULL DEFAULT NULL,
  `issue_count` int NULL DEFAULT NULL,
  `pull_count` int NULL DEFAULT NULL,
  `commit_count` int NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `lifespan_day` int NULL DEFAULT NULL,
  `is_selected` binary(1) NULL DEFAULT NULL,
  `is_famous` binary(1) NULL DEFAULT NULL,
  PRIMARY KEY (`repo_name`, `platform`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for churn_search_repos_2
-- ----------------------------
DROP TABLE IF EXISTS `churn_search_repos_2`;
CREATE TABLE `churn_search_repos_2`  (
  `repo_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `repo_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `repo_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `main_language` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `languages` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `star_count` int NULL DEFAULT NULL,
  `watch_count` int NULL DEFAULT NULL,
  `fork_count` int NULL DEFAULT NULL,
  `open_issue_pull_count` int NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `lifespan_day` int NULL DEFAULT NULL,
  `is_selected` binary(1) NULL DEFAULT NULL,
  `is_selected_final` binary(1) NULL DEFAULT NULL,
  `repo_type_manually` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `ai_type_manually` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_type` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_language_labels` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_repo_types` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_production_types` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `is_awesome` binary(1) NULL DEFAULT NULL,
  PRIMARY KEY (`repo_name`, `platform`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for churn_search_repos_final
-- ----------------------------
DROP TABLE IF EXISTS `churn_search_repos_final`;
CREATE TABLE `churn_search_repos_final`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `repo_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `repo_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `main_language` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `languages` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `star_count` int NULL DEFAULT NULL,
  `watch_count` int NULL DEFAULT NULL,
  `fork_count` int NULL DEFAULT NULL,
  `open_issue_pull_count` int NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `lifespan_day` int NULL DEFAULT NULL,
  `repo_type_manually` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `ai_type_manually` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_type` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_language_labels` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_repo_types` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `awesome_production_types` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `is_awesome` binary(1) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 30 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_commit
-- ----------------------------
DROP TABLE IF EXISTS `repo_commit`;
CREATE TABLE `repo_commit`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `commit_id` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '' COMMENT 'sha',
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `commit_time` datetime NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `commit_message` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_commit_time`(`commit_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_commit_id`(`commit_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 409323 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_commit_comment
-- ----------------------------
DROP TABLE IF EXISTS `repo_commit_comment`;
CREATE TABLE `repo_commit_comment`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `commit_id` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `comment_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `comment_time` datetime NULL DEFAULT NULL,
  `is_core_comment` binary(1) NULL DEFAULT NULL,
  `author_association` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_comment_time`(`comment_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_commit_id`(`commit_id`) USING BTREE,
  INDEX `join_comment_id`(`comment_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18233 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_commit_comment_extend
-- ----------------------------
DROP TABLE IF EXISTS `repo_commit_comment_extend`;
CREATE TABLE `repo_commit_comment_extend`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `comment_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `body` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `join_comment_id`(`comment_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5239 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_data_scope
-- ----------------------------
DROP TABLE IF EXISTS `repo_data_scope`;
CREATE TABLE `repo_data_scope`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_issue_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_issue_closed_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_issue_comment_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_pull_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_pull_merged_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_review_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_review_comment_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_commit_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_commit_comment_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_fork_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_star_scope` varchar(800) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_repo_id`(`repo_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for repo_fork
-- ----------------------------
DROP TABLE IF EXISTS `repo_fork`;
CREATE TABLE `repo_fork`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `fork_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `create_time` datetime NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `fork_full_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_create_time`(`create_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 166657 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_issue
-- ----------------------------
DROP TABLE IF EXISTS `repo_issue`;
CREATE TABLE `repo_issue`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `issue_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `issue_number` int UNSIGNED NOT NULL,
  `create_time` datetime NULL DEFAULT NULL,
  `update_time` datetime NULL DEFAULT NULL,
  `close_time` datetime NULL DEFAULT NULL,
  `is_core_issue` binary(1) NULL DEFAULT NULL,
  `is_locked_issue` binary(1) NULL DEFAULT NULL,
  `issue_state` varchar(7) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `issue_comment_count` int UNSIGNED NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `author_association` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_create_time`(`create_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_issue_id`(`issue_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 247357 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for repo_issue_closed
-- ----------------------------
DROP TABLE IF EXISTS `repo_issue_closed`;
CREATE TABLE `repo_issue_closed`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `issue_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NULL DEFAULT NULL,
  `close_time` datetime NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_close_time`(`close_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_issue_id`(`issue_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 232426 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_issue_comment
-- ----------------------------
DROP TABLE IF EXISTS `repo_issue_comment`;
CREATE TABLE `repo_issue_comment`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `issue_number` int UNSIGNED NOT NULL,
  `issue_comment_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `create_time` datetime NULL DEFAULT NULL,
  `update_time` datetime NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `author_association` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `polarity` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `is_core_issue_comment` binary(1) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_create_time`(`create_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_issue_comment_id`(`issue_comment_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1050167 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_issue_comment_extend
-- ----------------------------
DROP TABLE IF EXISTS `repo_issue_comment_extend`;
CREATE TABLE `repo_issue_comment_extend`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `issue_comment_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `issue_comment_body` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `join_issue_comment_id`(`issue_comment_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1040397 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_issue_extend
-- ----------------------------
DROP TABLE IF EXISTS `repo_issue_extend`;
CREATE TABLE `repo_issue_extend`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `issue_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `issue_labels` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `issue_title` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `issue_body` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `join_issue_id`(`issue_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 243590 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for repo_metadata
-- ----------------------------
DROP TABLE IF EXISTS `repo_metadata`;
CREATE TABLE `repo_metadata`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `repo_full_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_name` varchar(150) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `community_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `owner_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `owner_type` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_description` varchar(5000) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `main_language` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `languages` varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `languages_count` int UNSIGNED NOT NULL DEFAULT 0,
  `stars_count` int UNSIGNED NOT NULL DEFAULT 0,
  `forks_count` int UNSIGNED NOT NULL,
  `subscribers_count` int UNSIGNED NOT NULL DEFAULT 0,
  `size` int UNSIGNED NOT NULL DEFAULT 0,
  `create_time` datetime NULL DEFAULT NULL,
  `update_time` datetime NULL DEFAULT NULL,
  `repo_homepage` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `repo_license` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `join_repo_id`(`repo_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 30 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for repo_pull
-- ----------------------------
DROP TABLE IF EXISTS `repo_pull`;
CREATE TABLE `repo_pull`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `pull_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `pull_number` int UNSIGNED NOT NULL,
  `create_time` datetime NULL DEFAULT NULL,
  `update_time` datetime NULL DEFAULT NULL,
  `close_time` datetime NULL DEFAULT NULL,
  `merge_time` datetime NULL DEFAULT NULL,
  `is_core_pull` binary(1) NULL DEFAULT NULL,
  `is_locked_pull` binary(1) NULL DEFAULT NULL,
  `is_merged` binary(1) NULL DEFAULT NULL,
  `is_reviewed` binary(1) NULL DEFAULT NULL,
  `pull_state` varchar(7) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `pull_comment_count` int UNSIGNED NULL DEFAULT NULL,
  `pull_review_comment_count` int UNSIGNED NULL DEFAULT NULL,
  `core_review_count` int UNSIGNED NULL DEFAULT NULL,
  `core_review_comment_count` int UNSIGNED NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `author_association` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_create_time`(`create_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_pull_id`(`pull_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 135994 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_pull_extend
-- ----------------------------
DROP TABLE IF EXISTS `repo_pull_extend`;
CREATE TABLE `repo_pull_extend`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `pull_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `pull_title` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `pull_body` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `join_pull_id`(`pull_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 135344 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_pull_merged
-- ----------------------------
DROP TABLE IF EXISTS `repo_pull_merged`;
CREATE TABLE `repo_pull_merged`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `pull_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NULL DEFAULT NULL,
  `merge_time` datetime NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_merge_time`(`merge_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_pull_id`(`pull_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 135995 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_review
-- ----------------------------
DROP TABLE IF EXISTS `repo_review`;
CREATE TABLE `repo_review`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `pull_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `review_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `submit_time` datetime NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `author_association` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_submit_time`(`submit_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_pull_id`(`pull_id`) USING BTREE,
  INDEX `join_review_id`(`review_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 378726 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_review_comment
-- ----------------------------
DROP TABLE IF EXISTS `repo_review_comment`;
CREATE TABLE `repo_review_comment`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `pull_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `review_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `review_comment_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NULL DEFAULT NULL,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `author_association` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_create_time`(`create_time`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `join_pull_id`(`pull_id`) USING BTREE,
  INDEX `join_review_id`(`review_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 336772 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for repo_star
-- ----------------------------
DROP TABLE IF EXISTS `repo_star`;
CREATE TABLE `repo_star`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `repo_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `star_time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `normal_repo_user`(`user_id`, `repo_id`) USING BTREE,
  INDEX `normal_star_time`(`star_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 323566 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_data
-- ----------------------------
DROP TABLE IF EXISTS `user_data`;
CREATE TABLE `user_data`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` bigint UNSIGNED NOT NULL DEFAULT 0,
  `platform` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `user_login` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `user_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `followers_count` int UNSIGNED NOT NULL DEFAULT 0,
  `following_count` int UNSIGNED NOT NULL DEFAULT 0,
  `public_repos_count` int UNSIGNED NOT NULL DEFAULT 0,
  `user_type` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NULL DEFAULT NULL,
  `update_time` datetime NULL DEFAULT NULL,
  `user_company` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `user_location` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `user_email` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  `user_blog` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `join_user_id`(`user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 51531 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
