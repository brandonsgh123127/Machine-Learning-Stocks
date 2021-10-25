-- USE stocks;
-- SHOW TABLES;

-- FLUSH PRIVILEGES;
CREATE TABLE IF NOT EXISTS `Stocks`.`Stocks` (
  `id` VARBINARY(128) NOT NULL,
  `stock_id` VARBINARY(128) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
CREATE TABLE IF NOT EXISTS `Stocks`.`Stock` (
  `id` VARBINARY(128) NOT NULL,
  `stock` VARCHAR(5) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE TABLE IF NOT EXISTS `Stocks`.`Data` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATE NOT NULL,
  `open` VARCHAR(45) NULL,
  `high` VARCHAR(45) NULL,
  `low` VARCHAR(45) NULL,
  `close` VARCHAR(45) NULL,
  `adj-close` VARCHAR(45) NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE TABLE IF NOT EXISTS `Stocks`.`Study` (
  `study-id` VARBINARY(128) NOT NULL,
  `study` VARCHAR(32) NULL,
  PRIMARY KEY (`study-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`Study-Data` (
  `id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `data-id` VARBINARY(128) NOT NULL,
  `study-id` varbinary(128) NOT NULL,
  `val1` VARCHAR(45) NULL,
  `val2` VARCHAR(45) NULL,
  `val3` VARCHAR(45) NULL,
  `val4` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`Options` (
  `option-id` VARBINARY(128) NOT NULL,
  `option` VARCHAR(16) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`Options-Expiry` (
  `opt-expiry-id` VARBINARY(128) NOT NULL,
  `option-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `expiry` DATE NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`Options-Data` (
  `opt-data-id` VARBINARY(128) NOT NULL,
  `opt-expiry-id` VARBINARY(128) NOT NULL,
  `date` DATE NOT NULL,
  `bid` VARCHAR(45) NULL,
  `ask` VARCHAR(45) NULL,  
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

-- GRANT ALL ON `Stocks`.* TO 'admin-stock';
-- GRANT SELECT ON TABLE `Stocks`.* TO 'admin-stock';
-- GRANT SELECT, INSERT, TRIGGER ON TABLE `Stocks`.* TO 'admin-stock';
-- GRANT SELECT, INSERT, TRIGGER, UPDATE, DELETE,EXECUTE ON TABLE `Stocks`.* TO 'admin-stock';
-- CREATE USER 'customer' IDENTIFIED BY 'password';
-- GRANT SELECT ON TABLE `Stocks`.* TO 'customer';
use stocks;

# drop table stocks;
drop table stock;
drop table study;
drop table `data`;
drop table `study-data`;

DELETE FROM stock;
DELETE FROM data;
DELETE FROM `study-data`;
DELETE FROM study;


SELECT `stocks`.`data`.`date` FROM stocks.`data` INNER JOIN stocks.stock 
                        ON `stocks`.`data`.`stock-id` = `stocks`.`stock`.`id` 
                          AND `stocks`.`stock`.`stock` = "SPY" ;
SHOW TABLES FROM stocks;
select * from stocks.`data`;
select * from stocks.study;
select * from stocks.`study-data`;
-- ALTER TABLE stocks.`study-data` 
-- ADD COLUMN `val5` VARCHAR(45) NULL AFTER `val4`,
-- ADD COLUMN `val6` VARCHAR(45) NULL AFTER `val5`,
-- ADD COLUMN `val7` VARCHAR(45) NULL AFTER `val6`,
-- ADD COLUMN `val8` VARCHAR(45) NULL AFTER `val7`,
-- ADD COLUMN `val9` VARCHAR(45) NULL AFTER `val8`,
-- ADD COLUMN `val10` VARCHAR(45) NULL AFTER `val9`,
-- ADD COLUMN `val11` VARCHAR(45) NULL AFTER `val10`,
-- ADD COLUMN `val12` VARCHAR(45) NULL AFTER `val11`,
-- ADD COLUMN `val13` VARCHAR(45) NULL AFTER `val12`,
-- ADD COLUMN `val14` VARCHAR(45) NULL AFTER `val13`;


SELECT `stocks`.`data`.`date` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'SPY' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.`data`.`date`= DATE('2021-09-01');
SELECT `stock` FROM stocks.stock where `id` like 'SPY';
SELECT * FROM stocks.`data` INNER JOIN stocks.stock WHERE `stock-id` = stocks.stock.`id` and stocks.stock.`stock` = "ULTA" AND stocks.`data`.`date` = "2021-09-01";
ALTER TABLE stocks.stock ADD UNIQUE `stock-id` (id);
select * from stocks.`study-data`;
SELECT * FROM stocks.`data` INNER JOIN stocks.stock 
                        ON `stocks`.`data`.`stock-id` = `stocks`.`stock`.`id` 
                          AND stocks.stock.`stock` = "SPY"
                            INNER JOIN stocks.`study-data` ON
                            stocks.stock.`id` = stocks.`study-data`.`stock-id`
                            INNER JOIN stocks.`study` ON
                            stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
                            AND stocks.`study-data`.`study-id` = (AES_ENCRYPT('14', UNHEX(SHA2('14',512)))) 
                            AND stocks.`study-data`.`id` = (AES_ENCRYPT("2021-09-01 00:00:00SPY14", UNHEX(SHA2("2021-09-01 00:00:00SPY14",512))))
                            AND stocks.`data`.`data-id` = stocks.`study-data`.`data-id`;
SHOW INDEX FROM stocks.stock;

#select * from stocks.`data` where `stock-id` = (select data_id from stocks.stock where `stock` = 'AMD' LIMIT 1);
#select * from stocks.`data` where date >= '2020-03-03' and date <= '2021-04-22' and `stock-id` = (select `data_id` from stocks.stock where stock = 'SPY');
select * from stocks.data INNER JOIN stocks.stock ON `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.stock.stock = 'AXP' AND stocks.stock.id = AES_ENCRYPT('s', UNHEX(SHA2('s',512)));
SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id`, `stocks`.`data`.`date` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'AMC' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`;
SELECT * FROM stocks.`study-data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'SPY' AND stocks.`study-data`.`stock-id` = stocks.stock.id INNER JOIN stocks.`data` ON stocks.`study-data`.`data-id` = stocks.`data`.`data-id` INNER JOIN stocks.study ON stocks.study.study = "ema14" AND stocks.study.`study-id` = stocks.`study-data`.`study-id`;
SELECT * FROM stocks.`study-data`  INNER JOIN stocks.study ON stocks.study.study = "ema30";
SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'OCUL' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`;
SELECT `stocks`.`data`.`date` FROM stocks.`data` INNER JOIN stocks.stock 
                        ON `stock-id` = stocks.stock.`id` 
                          AND stocks.stock.`stock` = "SPY"
                           AND `stocks`.`data`.`date` = DATE("2021-10-01")
                           INNER JOIN stocks.`study-data` ON
                            stocks.stock.`id` = stocks.`study-data`.`stock-id`
                            INNER JOIN stocks.`study` ON
                            stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
                            AND stocks.`study-data`.`study-id` = (AES_ENCRYPT("fibonacci", UNHEX(SHA2("fibonacci",512))))
                            AND stocks.`data`.`data-id` = stocks.`study-data`.`data-id`;