-- USE stocks;
-- SHOW TABLES;

-- FLUSH PRIVILEGES;
CREATE TABLE IF NOT EXISTS `Stocks`.`Stock` (
  `id` VARBINARY(128) NOT NULL,
  `stock` VARCHAR(5) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE TABLE IF NOT EXISTS `Stocks`.`Data` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATE NOT NULL,
  `open` DOUBLE(12, 3) NOT NULL,
  `high` DOUBLE(12, 3) NOT NULL,
  `low` DOUBLE(12, 3) NOT NULL,
  `close` DOUBLE(12, 3) NOT NULL,
  `adj-close` DOUBLE(12, 3) NOT NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE TABLE IF NOT EXISTS `Stocks`.`Study` (
  `study-id` VARBINARY(128) NOT NULL,
  `study` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`study-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`Study-Data` (
  `id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `data-id` VARBINARY(128) NOT NULL,
  `study-id` varbinary(128) NOT NULL,
  `val1` DOUBLE(12, 3) NOT NULL,
  `val2` DOUBLE(12, 3) NULL,
  `val3` DOUBLE(12, 3) NULL,
  `val4` DOUBLE(12, 3) NULL,
  `val5` DOUBLE(12, 3) NULL,
  `val6` DOUBLE(12, 3) NULL,
  `val7` DOUBLE(12, 3) NULL,
  `val8` DOUBLE(12, 3) NULL,
  `val9` DOUBLE(12, 3) NULL,
  `val10` DOUBLE(12, 3) NULL,
  `val11` DOUBLE(12, 3) NULL,
  `val12` DOUBLE(12, 3) NULL,
  `val13` DOUBLE(12, 3) NULL,
  `val14` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6, 3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`Options` (
  `option-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `option-name` VARCHAR(64) NOT NULL,
  `type` VARCHAR(16) NOT NULL,
  PRIMARY KEY (`option-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`Options-Expiry` (
  `opt-expiry-id` VARBINARY(128) NOT NULL,
  `option-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `expiry` DATE NOT NULL,
  PRIMARY KEY (`opt-expiry-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

CREATE TABLE IF NOT EXISTS `Stocks`.`Options-Data` (
  `opt-data-id` VARBINARY(128) NOT NULL,
  `opt-expiry-id` VARBINARY(128) NOT NULL,
  `date` DATE NOT NULL,
  `bid` DOUBLE(12, 3) NOT NULL,
  `ask` DOUBLE(12, 3) NOT NULL,  
  PRIMARY KEY (`opt-data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;

use stocks;

# drop table stocks;
drop table stock;
drop table study;
drop table `data`;
drop table `study-data`;
drop table `nn-data`;
drop table `options`;
drop table `options-data`;
drop table `options-expiry`;

DELETE FROM stock;
DELETE FROM data;
DELETE FROM `study-data`;
DELETE FROM study;
DELETE FROM `nn-data`;


-- SELECT `stocks`.`data`.`date` FROM stocks.`data` INNER JOIN stocks.stock 
--                         ON `stocks`.`data`.`stock-id` = `stocks`.`stock`.`id` 
--                           AND `stocks`.`stock`.`stock` = "SPY" ;
-- SELECT `stocks`.`data`.`date` FROM stocks.`data` INNER JOIN stocks.stock 
--                         ON `stock-id` = stocks.stock.`id` 
--                           AND stocks.stock.`stock` = "'SPY'"
--                            AND `stocks`.`data`.`date` = DATE('2021-10-25')
--                            INNER JOIN stocks.`study-data` ON
--                             stocks.stock.`id` = stocks.`study-data`.`stock-id`
--                             AND stocks.`study-data`.`data-id` = stocks.`data`.`data-id`;
-- SELECT `stocks`.`data`.`date`,
--                         `stocks`.`study-data`.`val1`,`stocks`.`study-data`.`val2`,
--                         `stocks`.`study-data`.`val3`,`stocks`.`study-data`.`val4`,
--                         `stocks`.`study-data`.`val5`,`stocks`.`study-data`.`val6`,
--                         `stocks`.`study-data`.`val7`,`stocks`.`study-data`.`val8`,
--                         `stocks`.`study-data`.`val9`,`stocks`.`study-data`.`val10`,
--                         `stocks`.`study-data`.`val11`,`stocks`.`study-data`.`val12`,
--                         `stocks`.`study-data`.`val13`,`stocks`.`study-data`.`val14` 
--                          FROM stocks.`data` INNER JOIN stocks.stock 
--                         ON `stocks`.`data`.`stock-id` = stocks.stock.`id` 
--                           AND stocks.stock.`stock` = "SPY" 
--                            AND `stocks`.`data`.`date` = DATE("2021-10-25")
--                            INNER JOIN stocks.`study-data` ON
--                             stocks.stock.`id` = stocks.`study-data`.`stock-id`
--                             AND stocks.`study-data`.`data-id` = stocks.`data`.`data-id`;
SHOW TABLES FROM stocks;
select * from stocks.`data`;
select * from stocks.`stock`;
select * from stocks.study;
select * from stocks.`study-data`;
select * from stocks.`nn-data`;

-- SELECT `stocks`.`data`.`date` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'SPY' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.`data`.`date`= DATE('2021-09-01');
-- SELECT `stock`,`id` FROM stocks.stock where `id` like 'SPY';
-- SELECT * FROM stocks.`data` INNER JOIN stocks.stock WHERE `stock-id` = stocks.stock.`id` and stocks.stock.`stock` = "ULTA" AND stocks.`data`.`date` = "2021-09-01";
-- ALTER TABLE stocks.stock ADD UNIQUE `stock-id` (id);
-- select * from stocks.`study-data`;
-- SELECT * FROM stocks.`data` INNER JOIN stocks.stock 
--                         ON `stocks`.`data`.`stock-id` = `stocks`.`stock`.`id` 
--                           AND stocks.stock.`stock` = "SPY"
--                             INNER JOIN stocks.`study-data` ON
--                             stocks.stock.`id` = stocks.`study-data`.`stock-id`
--                             INNER JOIN stocks.`study` ON
--                             stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
--                             AND stocks.`study-data`.`study-id` = (AES_ENCRYPT('14', UNHEX(SHA2('14',512)))) 
--                             AND stocks.`study-data`.`id` = (AES_ENCRYPT("2021-09-01 00:00:00SPY14", UNHEX(SHA2("2021-09-01 00:00:00SPY14",512))))
--                             AND stocks.`data`.`data-id` = stocks.`study-data`.`data-id`;
SHOW INDEX FROM stocks.stock;

#select * from stocks.`data` where `stock-id` = (select data_id from stocks.stock where `stock` = 'AMD' LIMIT 1);
#select * from stocks.`data` where date >= '2020-03-03' and date <= '2021-04-22' and `stock-id` = (select `data_id` from stocks.stock where stock = 'SPY');
-- select * from stocks.data INNER JOIN stocks.stock ON `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.stock.stock = 'AXP' AND stocks.stock.id = AES_ENCRYPT('s', UNHEX(SHA2('s',512)));
-- SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id`, `stocks`.`data`.`date` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'AMC' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`;
-- SELECT * FROM stocks.`study-data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'SPY' AND stocks.`study-data`.`stock-id` = stocks.stock.id INNER JOIN stocks.`data` ON stocks.`study-data`.`data-id` = stocks.`data`.`data-id` INNER JOIN stocks.study ON stocks.study.study = "ema14" AND stocks.study.`study-id` = stocks.`study-data`.`study-id`;
-- SELECT * FROM stocks.`study-data`  INNER JOIN stocks.study ON stocks.study.study = "ema30";
-- SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'OCUL' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`;
-- SELECT `stocks`.`data`.`date` FROM stocks.`data` INNER JOIN stocks.stock 
--                         ON `stock-id` = stocks.stock.`id` 
--                           AND stocks.stock.`stock` = "SPY"
--                            AND `stocks`.`data`.`date` = DATE("2021-10-01")
--                            INNER JOIN stocks.`study-data` ON
--                             stocks.stock.`id` = stocks.`study-data`.`stock-id`
--                             INNER JOIN stocks.`study` ON
--                             stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
--                             AND stocks.`study-data`.`study-id` = (AES_ENCRYPT("fibonacci", UNHEX(SHA2("fibonacci",512))))
--                             AND stocks.`data`.`data-id` = stocks.`study-data`.`data-id`;