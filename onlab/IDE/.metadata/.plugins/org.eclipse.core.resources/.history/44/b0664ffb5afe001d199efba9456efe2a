/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <sht3x.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define RECEIVED_MESSAGE_SIZE 512	// Max size for ESP message
#define IP_ADDRESS "192.168.1.249"	// Server IP Address
#define PORT "9999"					// Server Port number
// AT command for connecting to server
#define SERVER_CONNECT "AT+CIPSTART=\"TCP\",\""IP_ADDRESS"\","PORT"\r\n"
#define WIFI_SSID "Telekom-2D6325"	// Local WIFI SSID
#define WIFI_PASS "4njteenm6s7cx4cb"// Local WIFI password
// AT command for connecting to wifi
#define WIFI_CONNECT "AT+CWJAP=\""WIFI_SSID"\",\""WIFI_PASS"\"\r\n"
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

I2C_HandleTypeDef hi2c4;
UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */
uint8_t rx_buffer;	// Global variable for UART callback func.
// Buffer to receive ESP messages
uint8_t received_message[RECEIVED_MESSAGE_SIZE] = {'\0'};
// Variables to store received sensor readings
float humidity = 0;
float temperature = 0;
// enum for FSM, controlls the program
enum state {	STATE_CONNECT_WIFI, STATE_CONNECT_SERVER, STATE_SEND_CIPSEND, STATE_SEND_DATA,
				STATE_SEND_ATE0, STATE_READY, STATE_ERROR, STATE_CONFIG};
// Global state variable
enum state current_state = STATE_READY;
// Sensor handle
sht3x_handle_t sht31 = {&hi2c4, SHT3X_I2C_DEVICE_ADDRESS_ADDR_PIN_LOW};
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_I2C4_Init(void);
/* USER CODE BEGIN PFP */

// UART Rx IRQ Callback func. Stores received data into received_message buffer
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart);

/* Finite State Machine to control states of program for example connecting to WIFI/Server,
 * Sending data, reading Sensor etc. */
enum state FSM(enum state current_state);

/* Used to receive message from ESP when delay is supected.
 * Waits until received_message contains array or until 5 seconds has
 * passed since calling or the function. Returns true if received_message
 * contains array string, returns false if 5 seconds has passed. */
bool AT_halt_until(const char *array);

/* Sends str string through UART to ESP and waits for response
 * defined in resp string. If transmit was successful and response
 * matches resp, return true, if response wasn't resp or 5 seconds
 * have passed, returns false. */
bool send_string(const char *str, const char *resp);

/* Configures ESP CIPMODE and CWMODE accordingly. Returns true if successful
 * configuration, returns false if configuration failed.*/
bool AT_config(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */
  SysTick_Config(SystemCoreClock/1000);	// Configure SysTick to IRQ every millisecond
  // Set IRQ priorities 0 is highest priority
  HAL_NVIC_SetPriority(SysTick_IRQn, 1, 0);
  // Incoming data always need to be handles -> highest priority!
  HAL_NVIC_SetPriority(USART2_IRQn, 0, 0);
  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  MX_I2C4_Init();
  /* USER CODE BEGIN 2 */
  // Initialise Sensor
  bool ok = sht3x_init(&sht31);
  if(!ok)
	  return 0;
  ok = sht3x_set_header_enable(&sht31, false);
  if(!ok)
  	  return 0;
  HAL_Delay(1000);	// Wait for Sensor to properly setup
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  // Always store previous state
  enum state prev_state;
  // Counts how many times has the program been in the same state consequently
  uint8_t error_counter = 0;
  while (1) {
	  // Consider being stuck in same state 5 times as error
	  if(error_counter == 5)
		  current_state = STATE_ERROR;
	  prev_state = current_state;
	  // Handle algorithm for current state and save the new state
	  current_state = FSM(current_state);
	  // New program state, reset ESP message buffer to prevent overflow and
	  // mixing of responses
	  if(prev_state != current_state){
		  memset(received_message, '\0', strlen((char*) received_message));
		  error_counter = 0;	// REset error counter
	  }
	  else
		  error_counter++;	// State hasn't changed
	  // If ESP is busy wait 1 second and try again
	  if(strstr((char*)received_message, "busy"))
		  HAL_Delay(1000);

  }
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  return 0;
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Supply configuration update enable
  */
  HAL_PWREx_ConfigSupply(PWR_LDO_SUPPLY);

  /** Configure the main internal regulator output voltage
  */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE3);

  while(!__HAL_PWR_GET_FLAG(PWR_FLAG_VOSRDY)) {}

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_DIV1;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2
                              |RCC_CLOCKTYPE_D3PCLK1|RCC_CLOCKTYPE_D1PCLK1;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.SYSCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB3CLKDivider = RCC_APB3_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_APB1_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_APB2_DIV1;
  RCC_ClkInitStruct.APB4CLKDivider = RCC_APB4_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief I2C4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C4_Init(void)
{

  /* USER CODE BEGIN I2C4_Init 0 */

  /* USER CODE END I2C4_Init 0 */

  /* USER CODE BEGIN I2C4_Init 1 */

  /* USER CODE END I2C4_Init 1 */
  hi2c4.Instance = I2C4;
  hi2c4.Init.Timing = 0x00707CBB;
  hi2c4.Init.OwnAddress1 = 0;
  hi2c4.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c4.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c4.Init.OwnAddress2 = 0;
  hi2c4.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c4.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c4.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c4) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c4, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c4, 0) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C4_Init 2 */

  /* USER CODE END I2C4_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */
  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  huart2.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart2.Init.ClockPrescaler = UART_PRESCALER_DIV1;
  huart2.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetTxFifoThreshold(&huart2, UART_TXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetRxFifoThreshold(&huart2, UART_RXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_DisableFifoMode(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */
  HAL_UART_Receive_IT(&huart2, &rx_buffer, 1);
  __HAL_UART_ENABLE_IT(&huart2, UART_IT_RXNE);

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOH, RST_Pin|GP0_Pin, GPIO_PIN_SET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, GP2_Pin|CHE_Pin, GPIO_PIN_SET);

  /*Configure GPIO pins : PB10 PB11 */
  GPIO_InitStruct.Pin = GPIO_PIN_10|GPIO_PIN_11;
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  GPIO_InitStruct.Alternate = GPIO_AF7_USART3;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pins : RST_Pin GP0_Pin */
  GPIO_InitStruct.Pin = RST_Pin|GP0_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOH, &GPIO_InitStruct);

  /*Configure GPIO pins : GP2_Pin CHE_Pin */
  GPIO_InitStruct.Pin = GP2_Pin|CHE_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
	// Store new data in received_message buffer
	strcat((char*)received_message, (char*)&rx_buffer);
	// Re-enable IRQ
	HAL_UART_Receive_IT(&huart2, &rx_buffer,  1);
}

enum state FSM(enum state current_state){
	char data_string[6];
	switch (current_state) {
		/* The starting state. Wait until ESP sends ready string to signal
		 * it is operating. Else signal possible error.*/
		case STATE_READY:
			if(AT_halt_until("ready\r\n"))
				return STATE_SEND_ATE0;
			return STATE_ERROR;
		/* After ESP startup disable echo mode on ESP. */
		case STATE_SEND_ATE0:
			if(send_string("ATE0\r\n", "OK\r\n"))
				return STATE_CONFIG;
			return STATE_ERROR;
		/* Configure ESP so it is able to connect to wifi and server. */
		case STATE_CONFIG:
			if(AT_config())
				return STATE_CONNECT_WIFI;
			return STATE_ERROR;
		/* Try and connect to local wifi. Tries two times! */
		case STATE_CONNECT_WIFI:
			if(send_string(WIFI_CONNECT, "OK\r\n"))
				return STATE_CONNECT_SERVER;
			else if(send_string(WIFI_CONNECT, "OK\r\n"))
				return STATE_CONNECT_SERVER;
			return STATE_ERROR;
		/* Try and connect to server. Tries two times! */
		case STATE_CONNECT_SERVER:
			if(send_string(SERVER_CONNECT, "OK\r\n"))
				return STATE_SEND_CIPSEND;
			else if(send_string(SERVER_CONNECT, "OK\r\n"))
				return STATE_SEND_CIPSEND;
			return STATE_ERROR;
		/* Wifi and server are connected. Prepare ESP to send 5 bytes
		 * of data. Assumes ambient temperature is greater than 10 and lower than 99.95
		 * as it will always result in 5 bytes of data to be sent. Server uses 'q' as
		 * data end character, so xx.xq is always 5 bytes. */
		case STATE_SEND_CIPSEND:
			// If can not receive data presume Sensor has been disconnected
			if(!sht3x_read_temperature_and_humidity(&sht31, &temperature, &humidity))
				return STATE_ERROR;
			if(send_string("AT+CIPSEND=5\r\n", "OK\r\n"))
				return STATE_SEND_DATA;
			else if(send_string("AT+CIPSEND=5\r\n", "OK\r\n"))
				return STATE_SEND_DATA;
			return STATE_ERROR;
		/* Try and send temperature data as characters.Assumes ambient temperature
		 * is greater than 10 and lower than 99.95. This is and infinite cycle in case
		 * of continuous failure to send data. main function handles this case. */
		case STATE_SEND_DATA:
			snprintf(data_string, 5, "%.1f", temperature);
			data_string[4] = 'q';	// End char
			if(send_string(data_string, "OK\r\n")){
				HAL_Delay(1000);
				return STATE_SEND_CIPSEND;
			}
			else
				return STATE_SEND_DATA;
		/* An error has occurred somewhere during running. Try to restore ESP.
		 * If this fails restart MCU. */
		case STATE_ERROR:
			if(send_string("AT+RESTORE\r\n", "ready\r\n"))
				return STATE_CONFIG;
			else
				NVIC_SystemReset();
		}
	return current_state;
}


bool AT_halt_until(const char *array){
	uint32_t start_time = uwTick;	// Save SysTick time upon entry
	  while(1){
		  if((uwTick - start_time) > 5000)// 5 seconds has passed
			  return false;
		  // If ESP is busy wait 1 second
		  if(strstr((char*)received_message, "busy") != NULL)
			  HAL_Delay(1000);
		  if(strstr((char*)received_message, array) != NULL)
			  return true;

	  }
}

bool AT_config(void){
	if(send_string("AT+CIPMODE=0\r\n", "OK\r\n")){
		memset(received_message, '\0', strlen((char*)received_message));
		if(send_string("AT+CWMODE=1\r\n", "OK\r\n"))
			return true;
	}
	return false;
}


bool send_string(const char *str, const char *resp) {
	if(HAL_UART_Transmit(&huart2, (uint8_t*)str, strlen(str), HAL_UART_TIMEOUT_VALUE) != HAL_OK){
		for(int i = 0; i < 3; i ++){ // In case of failure retry 3 times
			if(HAL_UART_Transmit(&huart2, (uint8_t*)str, strlen(str), HAL_UART_TIMEOUT_VALUE) == HAL_OK)
				break;
			else if(i == 2)
				return false;
		}
	}
	return AT_halt_until(resp);
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
