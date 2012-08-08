$(call inherit-product, device/samsung/crespo4g/full_crespo4g.mk)

PRODUCT_RELEASE_NAME := NS4G
# Inherit some common CM stuff.
$(call inherit-product, vendor/cm/config/common_full_phone.mk)

# Enhanced NFC
$(call inherit-product, vendor/cm/config/nfc_enhanced.mk)

PRODUCT_BUILD_PROP_OVERRIDES += PRODUCT_NAME=sojus BUILD_FINGERPRINT=google/sojus/crespo4g:4.1.1/JRO03C/398337:user/release-keys PRIVATE_BUILD_DESC="sojus-user 4.1.1 JRO03C 398337 release-keys" BUILD_NUMBER=398337

PRODUCT_NAME := cm_crespo4g
PRODUCT_DEVICE := crespo4g
PRODUCT_BRAND := Google
PRODUCT_MODEL := Nexus S 4G
PRODUCT_MANUFACTURER := Samsung

