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
FLUSH PRIVILEGES;
CREATE USER 'admin' IDENTIFIED BY 'Mgh8@091)21jKl14t';

GRANT ALL ON `Stocks`.* TO 'admin';
GRANT SELECT ON TABLE `Stocks`.* TO 'admin';
GRANT SELECT, INSERT, TRIGGER ON TABLE `Stocks`.* TO 'admin';
GRANT SELECT, INSERT, TRIGGER, UPDATE, DELETE,EXECUTE ON TABLE `Stocks`.* TO 'admin';
CREATE USER 'customer' IDENTIFIED BY 'password';
GRANT SELECT ON TABLE `Stocks`.* TO 'customer';

SHOW TABLES FROM stocks;