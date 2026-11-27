#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 GitHub Actions 编出来的 zImage 打回 BB06 的 boot.img
用法: python pack_boot.py <zImage路径> [输出路径]
"""
import os, sys, struct, shutil

ORIG_BOOT = r"D:\bb06\BB06阉割还原+优化包by酷安@Accepting\boot.img"
OUT_DEFAULT = r"D:\bb06\boot_new_kernel.img"

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("默认原厂 boot:", ORIG_BOOT)
        sys.exit(1)

    zimage_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else OUT_DEFAULT

    if not os.path.exists(zimage_path):
        print("找不到 zImage:", zimage_path); sys.exit(1)
    zimage = open(zimage_path, 'rb').read()
    print("新 zImage: %d 字节 (0x%X)" % (len(zimage), len(zimage)))

    boot = bytearray(open(ORIG_BOOT, 'rb').read())
    print("原厂 boot: %d 字节" % len(boot))
    if bytes(boot[:8]) != b'ANDROID!':
        print("不是 Android boot image"); sys.exit(1)

    old_ksz, kaddr, rsz, raddr = struct.unpack('<IIII', bytes(boot[8:24]))
    print("原 kernel: %d 字节 @ 0x%X" % (old_ksz, kaddr))
    print("原 ramdisk: %d 字节 @ 0x%X" % (rsz, raddr))

    PAGE = 2048
    # 原 boot 布局: header(1 page) + kernel(pages) + ramdisk(pages) + ...
    k_pages = (old_ksz + PAGE - 1) // PAGE
    r_off = PAGE + k_pages * PAGE
    ramdisk = bytes(boot[r_off:r_off + rsz])
    print("提取 ramdisk: %d 字节" % len(ramdisk))

    # 检查新 zImage 头
    print("新 zImage 头:", zimage[:8].hex())
    if zimage[0x24:0x28] != bytes.fromhex('18286f01'):
        print("  警告: 0x24 不是 0x016F2818，可能不是 ARM zImage")

    # 组装新 boot: header + new kernel + 原 ramdisk + 原剩下部分
    new_ksz = len(zimage)
    new_k_pages = (new_ksz + PAGE - 1) // PAGE
    # 保留 header 和 cmdline（前面 2048 字节），只改 kernel size 字段
    hdr = bytearray(boot[:PAGE])
    struct.pack_into('<I', hdr, 8, new_ksz)   # kernel size

    # kernel 后面补齐到 page
    k_pad = new_k_pages * PAGE - new_ksz
    out = bytes(hdr) + zimage + b'\x00' * k_pad + ramdisk

    # ramdisk 对齐
    r_pad = (PAGE - (len(ramdisk) % PAGE)) % PAGE
    out += b'\x00' * r_pad

    # 更新 ramdisk size（偏移 16）
    out = bytearray(out)
    struct.pack_into('<I', out, 16, rsz)

    open(out_path, 'wb').write(bytes(out))
    print("\n✓ 输出: %s" % out_path)
    print("  大小: %d 字节 (原 %d)" % (len(out), len(boot)))
    print("\n刷入参数:")
    print("  地址   1D80000")
    print("  长度   %X" % (((len(out) + 0xFFFFF) // 0x100000) * 0x100000))

if __name__ == '__main__':
    main()
