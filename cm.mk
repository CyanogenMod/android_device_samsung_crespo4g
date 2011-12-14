$(call inherit-product, device/samsung/crespo4g/full_crespo4g.mk)

PRODUCT_RELEASE_NAME := NS4G
# Inherit some common CM stuff.
$(call inherit-product, vendor/cm/config/common_full_phone.mk)

PRODUCT_BUILD_PROP_OVERRIDES += PRODUCT_NAME=sojus BUILD_ID=GWK74 BUILD_FINGERPRINT=google/sojus/crespo4g:2.3.7/GWK74/185293:user/release-keys PRIVATE_BUILD_DESC="sojus-user 2.3.7 GWK74 185293 release-keys" BUILD_NUMBER=185293

PRODUCT_NAME := cm_crespo4g
PRODUCT_DEVICE := crespo4g

