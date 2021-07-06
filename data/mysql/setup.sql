-- USE stocks;
-- SHOW TABLES;

-- FLUSH PRIVILEGES;
-- CREATE USER 'admin-stock' IDENTIFIED BY 'Mgh8@091)21jKl14t';
#CREATE TABLE IF NOT EXISTS `Stocks`.`Stocks` (
#  `id` VARBINARY(128) NOT NULL,
#  `stock_id` VARBINARY(128) NOT NULL,
#  PRIMARY KEY (`id`))
#ENGINE = InnoDB;
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
-- GRANT ALL ON `Stocks`.* TO 'admin-stock';
-- GRANT SELECT ON TABLE `Stocks`.* TO 'admin-stock';
-- GRANT SELECT, INSERT, TRIGGER ON TABLE `Stocks`.* TO 'admin-stock';
-- GRANT SELECT, INSERT, TRIGGER, UPDATE, DELETE,EXECUTE ON TABLE `Stocks`.* TO 'admin-stock';
-- CREATE USER 'customer' IDENTIFIED BY 'password';
-- GRANT SELECT ON TABLE `Stocks`.* TO 'customer';
use stocks;

# drop table stocks;
#drop table stock;
#drop table study;
#drop table data;
#drop table `study-data`;

SHOW TABLES FROM stocks;
select * from stocks.`data`;
select * from stocks.stock;
select * from stocks.study;
select * from stocks.`study-data`;


#select * from stocks.`data` where `stock-id` = (select data_id from stocks.stock where `stock` = 'AMD' LIMIT 1);
#select * from stocks.`data` where date >= '2020-03-03' and date <= '2021-04-22' and `stock-id` = (select `data_id` from stocks.stock where stock = 'SPY');
select * from stocks.data INNER JOIN stocks.stock ON `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.stock.stock = 'AXP' AND stocks.stock.id = AES_ENCRYPT('s', UNHEX(SHA2('s',512)));
SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id`, `stocks`.`data`.`date` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'NOC' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`;
SELECT * FROM stocks.`study-data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'RBLX' AND stocks.`study-data`.`stock-id` = stocks.stock.id;
SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'OCUL' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`;