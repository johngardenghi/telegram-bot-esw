-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: eswunb
-- ------------------------------------------------------
-- Server version	8.0.46-0ubuntu0.24.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administrador_estagio`
--

DROP TABLE IF EXISTS `administrador_estagio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administrador_estagio` (
  `telegram_id` varchar(45) NOT NULL,
  PRIMARY KEY (`telegram_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrador_estagio`
--

LOCK TABLES `administrador_estagio` WRITE;
/*!40000 ALTER TABLE `administrador_estagio` DISABLE KEYS */;
INSERT INTO `administrador_estagio` VALUES ('498325878'),('757482713');
/*!40000 ALTER TABLE `administrador_estagio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orientador_estagio`
--

DROP TABLE IF EXISTS `orientador_estagio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orientador_estagio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) DEFAULT NULL,
  `disponivel` tinyint DEFAULT NULL,
  `total_alunos_ativos` int DEFAULT NULL,
  `indisponivel_inicio` date DEFAULT NULL,
  `indisponivel_fim` date DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `contato` varchar(50) DEFAULT NULL,
  `sexo` varchar(1) DEFAULT NULL,
  `ativo` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orientador_estagio`
--

LOCK TABLES `orientador_estagio` WRITE;
/*!40000 ALTER TABLE `orientador_estagio` DISABLE KEYS */;
INSERT INTO `orientador_estagio` VALUES (1,'Cristiane Soares Ramos',1,6,'2026-02-01','2026-12-31','cristianesramos@unb.br',NULL,'F',1),(2,'Daniel Sundfeld Lima',0,20,'2026-01-01','2026-01-28','daniel.sundfeld@unb.br','Telegram @danielsundfeld','M',1),(3,'Edson Alves da Costa Junior',0,19,'2025-12-29','2026-02-13','edsonalves@unb.br',NULL,'M',1),(4,'Fernando William Cruz',1,21,'2026-06-15',NULL,'fwcruz@unb.br',NULL,'M',1),(5,'George Marsicano Correa',0,18,'2026-02-06','2026-03-06','georgemarsicano@unb.br',NULL,'M',1),(6,'Henrique Gomes de Moura',0,20,'2026-01-01','2026-01-27','hgmoura@unb.br','WhatsApp +55 61 99698-6360','M',1),(7,'John Lenon Cardoso Gardenghi',1,28,'2026-07-06','2026-07-26','john.gardenghi@unb.br','Telegram @johngardenghi','M',1),(8,'Mauricio Serrano',1,19,'2025-12-15','2026-02-04','serrano@unb.br',NULL,'M',1),(9,'Milene Serrano',1,21,'2025-12-15','2026-02-04','mileneserrano@unb.br',NULL,'F',1),(10,'Ricardo Ajax Dias Kosloski',1,21,'2026-01-16','2026-03-04','ricardoajax@unb.br',NULL,'M',1),(11,'Matheus Bernardini de Souza',1,21,'2025-12-29','2026-01-30','matheusbernardini@unb.br','Telegram @M_Bernardini','M',1),(12,'Vinicius de Carvalho Rispoli',0,19,'2025-12-27','2026-01-31','rispolivc@gmail.com','WhatsApp +55 61 99161-4745','M',1),(13,'Mario de Oliveira Andrade',1,9,'2026-02-02','2026-12-31','marioand@unb.br',NULL,'M',1),(14,'Ricardo Matos Chaim',1,13,'2025-10-01','2026-12-31','rmchaim@gmail.com','WhatsApp +55 61 99114-7801','M',1),(15,'Elaine Venson',1,19,NULL,NULL,'elainevenson@unb.br','Teams Elaine Venson','F',1),(16,'Sérgio Antônio Andrade de Freitas',1,16,'2026-05-03','2026-08-09','sergiofreitas@unb.br',NULL,'M',1),(17,'Wytler Cordeiro dos Santos',1,20,'2026-01-08','2026-02-10','wytler.cordeiro@unb.br','Telegram @Wytler','M',1),(18,'Fabiano Araujo Soares',1,19,'2026-01-08','2026-02-01','fabianosoares@unb.br','WhatsApp +55 61 99966-9700','M',1),(19,'Glauco Vitor Pedrosa',1,4,NULL,NULL,'glauco.pedrosa@unb.br',NULL,'M',0);
/*!40000 ALTER TABLE `orientador_estagio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `orientadores_ativos`
--

DROP TABLE IF EXISTS `orientadores_ativos`;
/*!50001 DROP VIEW IF EXISTS `orientadores_ativos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `orientadores_ativos` AS SELECT 
 1 AS `id`,
 1 AS `nome`,
 1 AS `disponivel`,
 1 AS `total_alunos_ativos`,
 1 AS `indisponivel_inicio`,
 1 AS `indisponivel_fim`,
 1 AS `email`,
 1 AS `contato`,
 1 AS `sexo`,
 1 AS `ativo`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `solicitacao_estagio`
--

DROP TABLE IF EXISTS `solicitacao_estagio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitacao_estagio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `orientador` int DEFAULT NULL,
  `aluno` varchar(100) DEFAULT NULL,
  `telegram_id` varchar(45) DEFAULT NULL,
  `data_hora` datetime DEFAULT NULL,
  `email_aluno` varchar(50) DEFAULT NULL,
  `telefone_aluno` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orientador_estagio_idx` (`orientador`),
  CONSTRAINT `orientador_estagio` FOREIGN KEY (`orientador`) REFERENCES `orientador_estagio` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=362 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `orientadores_ativos`
--

/*!50001 DROP VIEW IF EXISTS `orientadores_ativos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `orientadores_ativos` AS select `orientador_estagio`.`id` AS `id`,`orientador_estagio`.`nome` AS `nome`,`orientador_estagio`.`disponivel` AS `disponivel`,`orientador_estagio`.`total_alunos_ativos` AS `total_alunos_ativos`,`orientador_estagio`.`indisponivel_inicio` AS `indisponivel_inicio`,`orientador_estagio`.`indisponivel_fim` AS `indisponivel_fim`,`orientador_estagio`.`email` AS `email`,`orientador_estagio`.`contato` AS `contato`,`orientador_estagio`.`sexo` AS `sexo`,`orientador_estagio`.`ativo` AS `ativo` from `orientador_estagio` where ((`orientador_estagio`.`ativo` = 1) and (((`orientador_estagio`.`indisponivel_inicio` is not null) and (curdate() < `orientador_estagio`.`indisponivel_inicio`)) or ((`orientador_estagio`.`indisponivel_fim` is not null) and (curdate() > `orientador_estagio`.`indisponivel_fim`)) or ((`orientador_estagio`.`indisponivel_inicio` is null) and (`orientador_estagio`.`indisponivel_fim` is null)))) order by `orientador_estagio`.`nome` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-12 23:35:58
