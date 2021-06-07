-- USE stocks;
-- SHOW TABLES;

-- FLUSH PRIVILEGES;
-- CREATE USER 'admin-stock' IDENTIFIED BY 'Mgh8@091)21jKl14t';
CREATE TABLE IF NOT EXISTS `Stocks`.`Stocks` (
  `id` VARBINARY(128) NOT NULL,
  `stock_id` VARBINARY(128) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
CREATE TABLE IF NOT EXISTS `Stocks`.`Stock` (
  `id` VARBINARY(128) NOT NULL,
  `stock` VARCHAR(5) NULL,
  `data_id` VARBINARY(128) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
CREATE TABLE IF NOT EXISTS `Stocks`.`Data` (
  `id` VARBINARY(128) NOT NULL,
  `date` VARCHAR(45) NULL,
  `open` VARCHAR(45) NULL,
  `high` VARCHAR(45) NULL,
  `low` VARCHAR(45) NULL,
  `close` VARCHAR(45) NULL,
  `adj-close` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
-- GRANT ALL ON `Stocks`.* TO 'admin-stock';
-- GRANT SELECT ON TABLE `Stocks`.* TO 'admin-stock';
-- GRANT SELECT, INSERT, TRIGGER ON TABLE `Stocks`.* TO 'admin-stock';
-- GRANT SELECT, INSERT, TRIGGER, UPDATE, DELETE,EXECUTE ON TABLE `Stocks`.* TO 'admin-stock';
-- CREATE USER 'customer' IDENTIFIED BY 'password';
-- GRANT SELECT ON TABLE `Stocks`.* TO 'customer';
use stocks;
-- drop table stocks;
-- drop table stock;
-- drop table data;
SHOW TABLES FROM stocks;
INSERT IGNORE INTO `Stocks`.`Stocks`
SET `id` = AES_ENCRYPT('amc', UNHEX(SHA2('stock',512))),
`stock_id` = AES_ENCRYPT('amc', UNHEX(SHA2('stock-id',512)));
select id from `Stocks`.`Stocks`;
