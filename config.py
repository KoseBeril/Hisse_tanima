# ==========================================================
# BIST ENGINE PRO v1.0
# config.py
# ==========================================================

from tvDatafeed import Interval

# ----------------------------------------------------------
# GENEL
# ----------------------------------------------------------

TIMEFRAME = Interval.in_daily    # indikatörler ile analizi ise saatlik olarak yapıyoruz.
#TIMEFRAME = '1h'
BARS = 300
SEARCH_BARS = 120

# AI Score tarama sonucu filtrelenirken kullanılacak alt limit.
# Sadece bu puan ve üzerindeki hisseler sonuç listesine (CSV) eklenir.
MIN_SCORE = 70 

# ----------------------------------------------------------
# EMA / SMA
# ----------------------------------------------------------

EMA_LIST = [5, 8, 13, 20, 34, 50, 89, 100, 144, 200]
SMA_LIST = [20, 50, 100, 200]

# ----------------------------------------------------------
# RSI
# ----------------------------------------------------------

RSI_LENGTH = 14
RSI_EMA = 8
RSI_OVERSOLD = 30
RSI_RECOVERY = 40
RSI_OVERBOUGHT = 70

# ----------------------------------------------------------
# MACD
# ----------------------------------------------------------

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# ----------------------------------------------------------
# CCI / ROC / MOMENTUM / ADX / ATR
# ----------------------------------------------------------

CCI_LENGTH = 20
ROC_LENGTH = 10
MOMENTUM_LENGTH = 10
ADX_LENGTH = 14
ADX_LIMIT = 20
ATR_LENGTH = 14

# ----------------------------------------------------------
# STOCHASTIC
# ----------------------------------------------------------

STOCH_LENGTH = 14
STOCH_K_SMOOTH = 3
STOCH_D_SMOOTH = 3

# ----------------------------------------------------------
# HACİM & DİP
# ----------------------------------------------------------

RVOL_LIMIT = 1.20
VOL_MA = 20
DIP_LOOKBACK = 80
RSI_DIP = 32

# ----------------------------------------------------------
# FIBONACCI
# ----------------------------------------------------------
FIB_LOOKBACK = 100  # Fibonacci tepe/dip analizi için geriye dönük mum sayısı