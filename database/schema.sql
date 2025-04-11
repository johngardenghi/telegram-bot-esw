CREATE DATABASE eswbot;
USE eswbot;

CREATE TABLE `orientador_estagio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) DEFAULT NULL,
  `disponivel` tinyint DEFAULT NULL,
  `total_alunos_ativos` int DEFAULT NULL,
  `indisponivel_inicio` date DEFAULT NULL,
  `indisponivel_fim` date DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `solicitacao_estagio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `orientador` int DEFAULT NULL,
  `aluno` varchar(100) DEFAULT NULL,
  `telegram_id` varchar(45) DEFAULT NULL,
  `data_hora` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orientador_estagio_idx` (`orientador`),
  CONSTRAINT `orientador_estagio` FOREIGN KEY (`orientador`) REFERENCES `orientador_estagio` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO orientador_estagio VALUES
	('1', 'Cristiane Soares Ramos', '1', '0', NULL, NULL, 'cristianesramos@unb.br'),
	('2', 'Daniel Sundfeld Lima', '1', '0', NULL, NULL, 'daniel.sundfeld@unb.br'),
	('3', 'Edson Alves da Costa Junior', '1', '0', NULL, NULL, 'edsonalves@unb.br'),
	('4', 'Fernando William Cruz', '1', '0', NULL, NULL, 'fwcruz@unb.br'),
	('5', 'George Marsicano Correa', '1', '0', NULL, NULL, 'georgemarsicano@unb.br'),
	('6', 'Henrique Gomes de Moura', '1', '0', NULL, NULL, 'hgmoura@unb.br'),
	('7', 'John Lenon Cardoso Gardenghi', '1', '0', NULL, NULL, 'john.gardenghi@unb.br'),
	('8', 'Mauricio Serrano', '1', '0', NULL, NULL, 'serrano@unb.br'),
	('9', 'Milene Serrano', '1', '0', NULL, NULL, 'mileneserrano@unb.br'),
	('10', 'Ricardo Ajax Dias Kosloski', '1', '0', NULL, NULL, 'ricardoajax@unb.br');
