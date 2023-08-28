USE stocks;
SHOW TABLES;

-- FLUSH PRIVILEGES;
CREATE TABLE IF NOT EXISTS `Stocks`.`Stock` (
  `id` VARBINARY(128) NOT NULL,
  `stock` VARCHAR(5) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX stockid ON stocks.stock (id);

SELECT * 
FROM information_schema.tables
WHERE table_schema = 'stocks' 
    AND table_name = 'dailydata'
LIMIT 1;
SELECT UPDATE_TIME, TABLE_NAME
FROM   information_schema.tables
WHERE  TABLE_SCHEMA = 'stocks';
CREATE TABLE IF NOT EXISTS `Stocks`.`dailydata` (
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
CREATE INDEX `id-and-date` ON stocks.`dailydata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`dailydata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`dailydata` (`date`);


CREATE TABLE IF NOT EXISTS `Stocks`.`weeklydata` (
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
CREATE INDEX `id-and-date` ON stocks.`weeklydata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`weeklydata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`weeklydata` (`date`);


CREATE TABLE IF NOT EXISTS `Stocks`.`monthlydata` (
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
CREATE INDEX `id-and-date` ON stocks.`monthlydata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`monthlydata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`monthlydata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`yearlydata` (
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
CREATE INDEX `id-and-date` ON stocks.`yearlydata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`yearlydata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`yearlydata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`yearlydata` (
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
CREATE INDEX `id-and-date` ON stocks.`yearlydata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`yearlydata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`yearlydata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`15mdata` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATETIME NOT NULL,
  `open` DOUBLE(12, 3) NOT NULL,
  `high` DOUBLE(12, 3) NOT NULL,
  `low` DOUBLE(12, 3) NOT NULL,
  `close` DOUBLE(12, 3) NOT NULL,
  `adj-close` DOUBLE(12, 3) NOT NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `id-and-date` ON stocks.`15mdata` (`data-id`,`stock-id`,`date`);
DROP INDEX `id-and-date` ON stocks.`15mdata`;
CREATE INDEX `stockid-and-date` ON stocks.`15mdata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`15mdata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`30mdata` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATETIME NOT NULL,
  `open` DOUBLE(12, 3) NOT NULL,
  `high` DOUBLE(12, 3) NOT NULL,
  `low` DOUBLE(12, 3) NOT NULL,
  `close` DOUBLE(12, 3) NOT NULL,
  `adj-close` DOUBLE(12, 3) NOT NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `id-and-date` ON stocks.`30mdata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`30mdata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`30mdata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`5mdata` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATETIME NOT NULL,
  `open` DOUBLE(12, 3) NOT NULL,
  `high` DOUBLE(12, 3) NOT NULL,
  `low` DOUBLE(12, 3) NOT NULL,
  `close` DOUBLE(12, 3) NOT NULL,
  `adj-close` DOUBLE(12, 3) NOT NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `id-and-date` ON stocks.`5mdata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`5mdata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`5mdata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`1hdata` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATETIME NOT NULL,
  `open` DOUBLE(12, 3) NOT NULL,
  `high` DOUBLE(12, 3) NOT NULL,
  `low` DOUBLE(12, 3) NOT NULL,
  `close` DOUBLE(12, 3) NOT NULL,
  `adj-close` DOUBLE(12, 3) NOT NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `id-and-date` ON stocks.`1hdata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`1hdata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`1hdata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`60mdata` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATETIME NOT NULL,
  `open` DOUBLE(12, 3) NOT NULL,
  `high` DOUBLE(12, 3) NOT NULL,
  `low` DOUBLE(12, 3) NOT NULL,
  `close` DOUBLE(12, 3) NOT NULL,
  `adj-close` DOUBLE(12, 3) NOT NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `id-and-date` ON stocks.`60mdata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`60mdata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`60mdata` (`date`);


CREATE TABLE IF NOT EXISTS `Stocks`.`2hdata` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATETIME NOT NULL,
  `open` DOUBLE(12, 3) NOT NULL,
  `high` DOUBLE(12, 3) NOT NULL,
  `low` DOUBLE(12, 3) NOT NULL,
  `close` DOUBLE(12, 3) NOT NULL,
  `adj-close` DOUBLE(12, 3) NOT NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `id-and-date` ON stocks.`2hdata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`2hdata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`2hdata` (`date`);


CREATE TABLE IF NOT EXISTS `Stocks`.`4hdata` (
  `data-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `date` DATETIME NOT NULL,
  `open` DOUBLE(12, 3) NOT NULL,
  `high` DOUBLE(12, 3) NOT NULL,
  `low` DOUBLE(12, 3) NOT NULL,
  `close` DOUBLE(12, 3) NOT NULL,
  `adj-close` DOUBLE(12, 3) NOT NULL,
  PRIMARY KEY (`data-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `id-and-date` ON stocks.`4hdata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`4hdata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`4hdata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`2ddata` (
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
CREATE INDEX `id-and-date` ON stocks.`2ddata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`2ddata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`2ddata` (`date`);

CREATE TABLE IF NOT EXISTS `Stocks`.`4ddata` (
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
CREATE INDEX `id-and-date` ON stocks.`4ddata` (`data-id`,`stock-id`,`date`);
CREATE INDEX `stockid-and-date` ON stocks.`4ddata` (`stock-id`,`date`);
CREATE INDEX `date` ON stocks.`4ddata` (`date`);


CREATE TABLE IF NOT EXISTS `Stocks`.`Study` (
  `study-id` VARBINARY(128) NOT NULL,
  `study` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`study-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `studyid` ON stocks.`study` (`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`Daily-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`Daily-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`Weekly-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`Weekly-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`Monthly-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`Monthly-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`Yearly-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`Yearly-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`15m-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`15m-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`5m-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`5m-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`30m-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`30m-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`60m-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`60m-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`1h-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`1h-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`2h-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
  `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`2h-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`4h-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
    `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`4h-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);



CREATE TABLE IF NOT EXISTS `Stocks`.`2d-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
    `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`2d-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`4d-Study-Data` (
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
  `val15` DOUBLE(12, 3) NULL,
  `val16` DOUBLE(12, 3) NULL,
    `val17` DOUBLE(12, 3) NULL,
  `val18` DOUBLE(12, 3) NULL,
  `val19` DOUBLE(12, 3) NULL,
  `val20` DOUBLE(12, 3) NULL,
  `val21` DOUBLE(12, 3) NULL,
  `val22` DOUBLE(12, 3) NULL,
  `val23` DOUBLE(12, 3) NULL,
  `val24` DOUBLE(12, 3) NULL,
  `val25` DOUBLE(12, 3) NULL,
  `val26` DOUBLE(12, 3) NULL,
  `val27` DOUBLE(12, 3) NULL,
  `val28` DOUBLE(12, 3) NULL,
  `val29` DOUBLE(12, 3) NULL,
  `val30` DOUBLE(12, 3) NULL,
  `val31` DOUBLE(12, 3) NULL,
  `val32` DOUBLE(12, 3) NULL,
  `val33` DOUBLE(12, 3) NULL,
  `val34` DOUBLE(12, 3) NULL,
  `val35` DOUBLE(12, 3) NULL,
  `val36` DOUBLE(12, 3) NULL,
  `val37` DOUBLE(12, 3) NULL,
  `val38` DOUBLE(12, 3) NULL,
  `val39` DOUBLE(12, 3) NULL,
  `val40` DOUBLE(12, 3) NULL,
  `val41` DOUBLE(12, 3) NULL,
  `val42` DOUBLE(12, 3) NULL,
  `val43` DOUBLE(12, 3) NULL,
  `val44` DOUBLE(12, 3) NULL,
  `val45` DOUBLE(12, 3) NULL,
  `val46` DOUBLE(12, 3) NULL,
  `val47` DOUBLE(12, 3) NULL,
  `val48` DOUBLE(12, 3) NULL,
  `val49` DOUBLE(12, 3) NULL,
  `val50` DOUBLE(12, 3) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`4d-Study-Data` (`id`,`stock-id`,`data-id`,`study-id`);


CREATE TABLE IF NOT EXISTS `Stocks`.`Daily-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`Daily-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`Daily-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`Daily-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`Weekly-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`Weekly-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`Weekly-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`Weekly-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`Monthly-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`Monthly-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`Monthly-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`Monthly-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`Yearly-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`Yearly-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`Yearly-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`Yearly-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`15m-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`15m-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`15m-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`15m-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`5m-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`5m-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`5m-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`5m-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`30m-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`30m-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`30m-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`30m-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`60m-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`60m-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`60m-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`60m-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`1h-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`1h-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`1h-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`1h-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`2h-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`2h-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`2h-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`2h-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`4h-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`4h-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`4h-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`4h-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`2d-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`2d-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`2d-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`2d-NN-Data` (`stock-id`);

CREATE TABLE IF NOT EXISTS `Stocks`.`4d-NN-Data` (
  `nn-id` VARBINARY(128) NOT NULL,
  `stock-id` VARBINARY(128) NOT NULL,
  `from-date-id` VARBINARY(128) NOT NULL,
  `to-date-id` VARBINARY(128) NOT NULL,
  `model` VARCHAR(45) NULL,
  `open` DOUBLE(6, 3) NULL,
  `close` DOUBLE(6, 3) NULL,
  `range` DOUBLE(6,3) NULL,
  PRIMARY KEY (`nn-id`))
ENGINE = InnoDB CHARACTER SET latin1 default CHARACTER SET latin1;
CREATE INDEX `ids` ON stocks.`4d-NN-Data` (`nn-id`,`stock-id`,`from-date-id`,`to-date-id`);
CREATE INDEX `from-to-model` ON stocks.`4d-NN-Data` (`from-date-id`,`to-date-id`,`model`);
CREATE INDEX `stockid` ON stocks.`4d-NN-Data` (`stock-id`);


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
drop table `15mdata`;
drop table `30mdata`;
drop table `5mdata`;
drop table `1hdata`;
drop table `2hdata`;
drop table `4hdata`;
use stocks;
drop table `daily-study-data`;
drop table `weekly-study-data`;
drop table `monthly-study-data`;
drop table `yearly-study-data`;
drop table `5m-study-data`;
drop table `15m-study-data`;
drop table `30m-study-data`;
drop table `60m-study-data`;
drop table `2h-study-data`;
drop table `4h-study-data`;
drop table `2d-study-data`;
drop table `4d-study-data`;
drop table `nn-data`;
drop table `options`;
drop table `options-data`;
drop table `options-expiry`;

DELETE FROM stock;
DELETE FROM dailydata;
DELETE FROM weeklydata;
DELETE FROM monthlydata;
DELETE FROM yearlydata;

DELETE FROM `daily-study-data`;
DELETE FROM `weekly-study-data`;
DELETE FROM `monthly-study-data`;
DELETE FROM `yearly-study-data`;
DELETE FROM study;
DELETE FROM `nn-data`;
DELETE FROM `15mdata`;

DELETE FROM `options`;
DELETE FROM `options-data`;
DELETE FROM `options-expiry`;

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
select * from stocks.`dailydata` USE INDEX (`id-and-date`) ;
select `open`,`high`,`low`,`close` from stocks.`data` USE INDEX (`id-and-date`,`date`) INNER JOIN stocks.`stock` USE INDEX(`stockid`) on `date` = DATE('2021-11-04') and `id` = stocks.`data`.`stock-id`;
select * from stocks.`stock` USE INDEX (`stockid`);
select * from stocks.study USE INDEX (`studyid`);
select * from stocks.`study-data` USE INDEX (`ids`);
select * from stocks.`nn-data` USE INDEX (`ids`);
select * from stocks.`nn-data`;
select * from stocks.`weeklydata`;
select `date` from stocks.`15mdata`;
select * from stocks.`15mdata`;
SELECT `stocks`.`15mdata`.`data-id` from stocks.`15mdata`;
SELECT `stocks`.`15mdata`.`data-id`,
                             `stocks`.`15mdata`.`stock-id` FROM `stocks`.`15mdata` USE INDEX (`id-and-date`)
                            INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.`stock`.`stock` = "AAPL" AND `stocks`.`stock`.`id` = `stocks`.`15mdata`.`stock-id`
                             AND `stocks`.`15mdata`.`date`>= '2022-09-19 09:30:00'
                             AND `stocks`.`15mdata`.`date`<= '2022-09-19 16:00:00'
                             ORDER BY `stocks`.`15mdata`.`date` ASC;


select * from stocks.`data` inner join `stocks`.`stock` ON `stocks`.stock.stock = 'AXP' AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`  and stocks.`data`.`date` = DATE('2008-11-07');
SELECT `stocks`.`study-data`.* FROM `stocks`.`study-data` INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = 'PEP' AND `stocks`.`stock`.`id` = `stocks`.`study-data`.`stock-id` INNER JOIN stocks.`data` on stocks.`data`.`stock-id` = stocks.stock.`id` and stocks.`data`.`date` = DATE('2015-11-23') and stocks.`data`.`data-id` =  stocks.`study-data`.`data-id`	;
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
select * from stocks.`study-data` inner join stocks.stock on stocks.`study-data`.`stock-id` = stocks.`stock`.`id` and stock.stock = 'DOCU';
select stocks.`study-data`.val1, stocks.`study`.study from stocks.`study` INNER JOIN stocks.`study-data` 
            ON stocks.`study-data`.`study-id` = stocks.`study`.`study-id` INNER JOIN stocks.`data` ON
             stocks.`study-data`.`data-id` = `stocks`.`data`.`data-id`
              AND stocks.`data`.date >= DATE('2021-05-09')
               AND stocks.`data`.date <= DATE('2021-06-18')
                AND stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
                AND stocks.`study`.`study` like 'ema%' 
             INNER JOIN stocks.stock ON stocks.stock.`id` = stocks.`data`.`stock-id` AND stocks.stock.stock = 'DOCU';
INSERT INTO stocks.stock (id, stock) VALUES (AES_ENCRYPT('test', 'test'),'test');
SELECT `stocks`.`dailydata`.`data-id`,`stocks`.`dailydata`.`date` FROM `stocks`.`dailydata` USE INDEX (`id-and-date`) INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = 'SPY' AND `stocks`.`stock`.`id` = `stocks`.`dailydata`.`stock-id` AND `stocks`.`dailydata`.`date`>= DATE('2012-11-02') AND `stocks`.`dailydata`.`date`<= DATE('2013-03-28') ORDER BY stocks.`dailydata`.`date` ASC;
SELECT `stocks`.`stock`.`id` FROM stocks.`stock` USE INDEX (`stockid`) WHERE `stocks`.`stock`.`stock` = 'SPY';
SELECT `stocks`.`weeklydata`.`data-id`,`stocks`.`weeklydata`.`date` FROM stocks.`weeklydata` USE INDEX (`stockid-and-date`) WHERE stocks.`weeklydata`.`stock-id` = (SELECT `stocks`.`stock`.`id` FROM stocks.`stock` USE INDEX (`stockid`) WHERE `stocks`.`stock`.`stock` = 'SPY') AND stocks.`weeklydata`.`date` >= DATE('2022-01-21');