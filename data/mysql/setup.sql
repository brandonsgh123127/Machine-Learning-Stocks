-- USE stocks;
-- SHOW TABLES;
CREATE TABLE IF NOT EXISTS `Stocks`.`Stocks` (
  `id` INT NOT NULL,
  `stock_id` INT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
CREATE TABLE IF NOT EXISTS `Stocks`.`Stock` (
  `id` INT NOT NULL,
  `stock` VARCHAR(45) NULL,
  `data_id` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
CREATE TABLE IF NOT EXISTS `Stocks`.`Data` (
  `id` INT NOT NULL,
  `date` VARCHAR(45) NULL,
  `open` VARCHAR(45) NULL,
  `high` VARCHAR(45) NULL,
  `low` VARCHAR(45) NULL,
  `close` VARCHAR(45) NULL,
  `adj-close` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
SHOW TABLES FROM stocks;