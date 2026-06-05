-- Web中台AI系统 数据库建表SQL
-- 存储引擎：InnoDB，字符集：utf8mb4
-- 金额字段使用DECIMAL避免浮点精度问题

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 1. 项目表 project
-- ----------------------------
DROP TABLE IF EXISTS `project`;
CREATE TABLE `project` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '项目ID',
  `project_name` VARCHAR(200) NOT NULL COMMENT '项目名称',
  `customer_project_name` VARCHAR(200) DEFAULT NULL COMMENT '客户内部项目名',
  `customer_project_code` VARCHAR(100) DEFAULT NULL COMMENT '客户内部项目编号',
  `company_name` VARCHAR(200) DEFAULT NULL COMMENT '公司名称',
  `address` VARCHAR(500) DEFAULT NULL COMMENT '项目地址',
  `lng` DECIMAL(10,6) DEFAULT NULL COMMENT '经度',
  `lat` DECIMAL(10,6) DEFAULT NULL COMMENT '纬度',
  `contract_amount` DECIMAL(15,2) DEFAULT NULL COMMENT '合同金额',
  `payment_term` VARCHAR(200) DEFAULT NULL COMMENT '付款周期',
  `project_type` ENUM('day_project','package_project') NOT NULL COMMENT '项目类型：人天项目/整包项目',
  `fixed_package_amount` DECIMAL(15,2) DEFAULT NULL COMMENT '固定包干总价',
  `customer_surplus_man_day` INT DEFAULT 0 COMMENT '客户溢量人天',
  `surplus_man_day_status` ENUM('pending','finished','cancel') DEFAULT 'pending' COMMENT '溢量兑付状态',
  `status` ENUM('active','suspended','finished','cancelled') DEFAULT 'active' COMMENT '项目状态',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `idx_project_type` (`project_type`),
  INDEX `idx_project_status` (`status`),
  INDEX `idx_project_name` (`project_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目表';

-- ----------------------------
-- 2. 合同回款表 contract_payment
-- ----------------------------
DROP TABLE IF EXISTS `contract_payment`;
CREATE TABLE `contract_payment` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '回款记录ID',
  `project_id` INT NOT NULL COMMENT '项目ID',
  `contract_no` VARCHAR(100) NOT NULL COMMENT '合同编号',
  `total_amount` DECIMAL(15,2) DEFAULT 0 COMMENT '合同总金额',
  `paid_amount` DECIMAL(15,2) DEFAULT 0 COMMENT '已回款金额',
  `unpaid_amount` DECIMAL(15,2) DEFAULT 0 COMMENT '未回款金额',
  `payment_status` ENUM('unpaid','partial','paid') DEFAULT 'unpaid' COMMENT '回款状态',
  `expect_pay_date` DATETIME DEFAULT NULL COMMENT '预计回款日期',
  `last_mail_check_time` DATETIME DEFAULT NULL COMMENT '最近邮件核查时间',
  `project_surplus_income` DECIMAL(15,2) DEFAULT 0 COMMENT '溢量过路流水营收',
  `project_cost_man_day` DECIMAL(15,2) DEFAULT 0 COMMENT '项目人力总成本',
  `project_cost_travel` DECIMAL(15,2) DEFAULT 0 COMMENT '项目差旅总成本',
  `project_gross_profit` DECIMAL(15,2) DEFAULT 0 COMMENT '项目毛利',
  `package_cost_budget` DECIMAL(15,2) DEFAULT NULL COMMENT '整包成本预算',
  `package_cost_surplus` DECIMAL(15,2) DEFAULT NULL COMMENT '整包成本剩余',
  `package_risk_status` ENUM('normal','warning','loss') DEFAULT 'normal' COMMENT '整包风险状态',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_contract_no` (`contract_no`),
  INDEX `idx_contract_project` (`project_id`),
  CONSTRAINT `fk_cp_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='合同回款表';

-- ----------------------------
-- 3. 员工档案表 staff
-- ----------------------------
DROP TABLE IF EXISTS `staff`;
CREATE TABLE `staff` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '员工ID',
  `feishu_uid` VARCHAR(100) DEFAULT NULL COMMENT '飞书UID',
  `name` VARCHAR(50) NOT NULL COMMENT '姓名',
  `department` VARCHAR(100) DEFAULT NULL COMMENT '部门',
  `staff_level` ENUM('p0','p1-1','p1-2','p1-3') NOT NULL COMMENT '职级',
  `base_salary` DECIMAL(15,2) DEFAULT 0 COMMENT '底薪',
  `default_day_price` INT NOT NULL COMMENT '默认对外结算单价',
  `default_day_commission` INT NOT NULL COMMENT '默认人天提成单价',
  `day_commission_rate` DECIMAL(5,4) DEFAULT 0 COMMENT '人天提成比例',
  `package_commission_rate` DECIMAL(5,4) DEFAULT 0 COMMENT '整包提成比例',
  `status` ENUM('active','inactive','resigned') DEFAULT 'active' COMMENT '状态',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_feishu_uid` (`feishu_uid`),
  INDEX `idx_staff_level` (`staff_level`),
  INDEX `idx_staff_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='员工档案表';

-- ----------------------------
-- 4. 项目人员配置表 project_staff_config
-- ----------------------------
DROP TABLE IF EXISTS `project_staff_config`;
CREATE TABLE `project_staff_config` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `project_id` INT NOT NULL COMMENT '项目ID',
  `staff_id` INT NOT NULL COMMENT '员工ID',
  `custom_day_commission` INT DEFAULT NULL COMMENT '自定义人天提成单价',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_project_staff` (`project_id`, `staff_id`),
  INDEX `idx_psc_project` (`project_id`),
  INDEX `idx_psc_staff` (`staff_id`),
  CONSTRAINT `fk_psc_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_psc_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目人员提成配置表';

-- ----------------------------
-- 5. 签到记录表 sign_record
-- ----------------------------
DROP TABLE IF EXISTS `sign_record`;
CREATE TABLE `sign_record` (
  `task_id` VARCHAR(50) NOT NULL COMMENT '任务ID',
  `staff_id` INT NOT NULL COMMENT '员工ID',
  `project_id` INT NOT NULL COMMENT '项目ID',
  `sign_lng` DECIMAL(10,6) DEFAULT NULL COMMENT '签到经度',
  `sign_lat` DECIMAL(10,6) DEFAULT NULL COMMENT '签到纬度',
  `sign_address` VARCHAR(500) DEFAULT NULL COMMENT '签到地址',
  `sign_status` ENUM('pending','success','failed') DEFAULT 'pending' COMMENT '签到状态',
  `screenshot_url` VARCHAR(500) DEFAULT NULL COMMENT '截图URL',
  `sign_time` DATETIME DEFAULT NULL COMMENT '签到时间',
  `source` VARCHAR(20) NOT NULL DEFAULT 'web' COMMENT '来源：feishu/web/system',
  PRIMARY KEY (`task_id`),
  INDEX `idx_sign_staff` (`staff_id`),
  INDEX `idx_sign_project` (`project_id`),
  INDEX `idx_sign_time` (`sign_time`),
  INDEX `idx_sign_status` (`sign_status`),
  CONSTRAINT `fk_sr_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sr_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='签到记录表';

-- ----------------------------
-- 6. 报销明细表 reimburse
-- ----------------------------
DROP TABLE IF EXISTS `reimburse`;
CREATE TABLE `reimburse` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '报销ID',
  `staff_id` INT NOT NULL COMMENT '员工ID',
  `project_id` INT NOT NULL COMMENT '项目ID',
  `invoice_no` VARCHAR(100) NOT NULL COMMENT '发票号',
  `invoice_amount` DECIMAL(15,2) NOT NULL COMMENT '发票金额',
  `invoice_date` DATETIME DEFAULT NULL COMMENT '发票日期',
  `file_url` VARCHAR(500) DEFAULT NULL COMMENT '文件URL',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `reimburse_type` ENUM('default','deduction') DEFAULT 'default' COMMENT '报销类型',
  `check_status` ENUM('pending','approved','rejected') DEFAULT 'pending' COMMENT '审核状态',
  `settle_status` ENUM('pending','settled','cancelled') DEFAULT 'pending' COMMENT '结算状态',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `idx_reimburse_staff` (`staff_id`),
  INDEX `idx_reimburse_project` (`project_id`),
  INDEX `idx_reimburse_type` (`reimburse_type`),
  INDEX `idx_reimburse_settle` (`settle_status`),
  CONSTRAINT `fk_reimburse_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_reimburse_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报销明细表';

-- ----------------------------
-- 7. 项目提成表 staff_commission
-- ----------------------------
DROP TABLE IF EXISTS `staff_commission`;
CREATE TABLE `staff_commission` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '提成ID',
  `staff_id` INT NOT NULL COMMENT '员工ID',
  `project_id` INT NOT NULL COMMENT '项目ID',
  `payment_id` INT DEFAULT NULL COMMENT '回款ID',
  `commission_type` ENUM('day','both','package') NOT NULL COMMENT '提成类型',
  `day_commission_amount` DECIMAL(15,2) DEFAULT 0 COMMENT '人天提成金额',
  `package_bonus_amount` DECIMAL(15,2) DEFAULT 0 COMMENT '整包奖金金额',
  `total_commission` DECIMAL(15,2) DEFAULT 0 COMMENT '总提成',
  `rate` DECIMAL(5,4) DEFAULT NULL COMMENT '提成比例',
  `project_day_commission` INT DEFAULT 0 COMMENT '项目人天数',
  `settle_status` ENUM('pending','settled','cancelled') DEFAULT 'pending' COMMENT '结算状态',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `idx_sc_staff` (`staff_id`),
  INDEX `idx_sc_project` (`project_id`),
  INDEX `idx_sc_payment` (`payment_id`),
  INDEX `idx_sc_settle` (`settle_status`),
  CONSTRAINT `fk_sc_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sc_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sc_payment` FOREIGN KEY (`payment_id`) REFERENCES `contract_payment` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目提成表';

-- ----------------------------
-- 8. 工资单表 salary_bill
-- ----------------------------
DROP TABLE IF EXISTS `salary_bill`;
CREATE TABLE `salary_bill` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '工资单ID',
  `staff_id` INT NOT NULL COMMENT '员工ID',
  `month` VARCHAR(7) NOT NULL COMMENT '月份YYYY-MM',
  `base_salary_total` DECIMAL(15,2) DEFAULT 0 COMMENT '底薪合计',
  `day_commission_total` DECIMAL(15,2) DEFAULT 0 COMMENT '人天提成合计',
  `package_bonus_total` DECIMAL(15,2) DEFAULT 0 COMMENT '整包奖金合计',
  `commission_total` DECIMAL(15,2) DEFAULT 0 COMMENT '提成合计',
  `reimburse_total` DECIMAL(15,2) DEFAULT 0 COMMENT '报销合计',
  `final_salary` DECIMAL(15,2) DEFAULT 0 COMMENT '最终薪资',
  `status` ENUM('draft','confirmed','paid') DEFAULT 'draft' COMMENT '状态',
  `file_url` VARCHAR(500) DEFAULT NULL COMMENT '工资单文件URL',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_staff_month` (`staff_id`, `month`),
  INDEX `idx_sb_staff` (`staff_id`),
  INDEX `idx_sb_month` (`month`),
  INDEX `idx_sb_status` (`status`),
  CONSTRAINT `fk_sb_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工资单表';

SET FOREIGN_KEY_CHECKS = 1;