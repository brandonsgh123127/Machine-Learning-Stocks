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
#drop table data;
#drop table `study-data`;
SHOW TABLES FROM stocks;
#INSERT INTO stocks.stock (id, stock, data_id) VALUES (AES_ENCRYPT('AMC', UNHEX(SHA2('stock',512))),'AMC',AES_ENCRYPT('AMC', UNHEX(SHA2('stock-id',512))));
#INSERT INTO stocks.`data` (id, `date`,`open`,high,low,`close`,`adj-close`) VALUES (AES_ENCRYPT('AMC', UNHEX(SHA2('stock-id',512))),DATE('2020-08-08'),0,0,0,0,0);

#SELECT * FROM stocks.stock WHERE stock = 'AMD';
# SET `id` = AES_ENCRYPT('amc', UNHEX(SHA2('stock',512))),
#`stock_id` = AES_ENCRYPT('amc', UNHEX(SHA2('stock-id',512)));
#delete from stocks.data where open like 0;
#select * from stocks.data;
#select data_id from stocks.stock where `stock` = 'SPY' LIMIT 1;
#select * from stocks.`data`;
select * from stocks.stock;
#select * from stocks.`data` where `stock-id` = (select data_id from stocks.stock where `stock` = 'AMD' LIMIT 1);
#select * from stocks.`data` where date >= '2020-03-03' and date <= '2021-04-22' and `stock-id` = (select `data_id` from stocks.stock where stock = 'SPY');
select * from stocks.stock INNER JOIN stocks.data ON `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.stock.stock = 'SPY';
SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'SPY' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` ;