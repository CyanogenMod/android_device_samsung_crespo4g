ifeq ($(TARGET_DEVICE),crespo4g)

LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE_TAGS := eng
LOCAL_C_INCLUDES += bootable/recovery
LOCAL_SRC_FILES := recovery_updater.c

# should match TARGET_RECOVERY_UPDATER_LIB set in BoardConfig.mk
LOCAL_MODULE := librecovery_updater_crespo4g

include $(BUILD_STATIC_LIBRARY)

endif
