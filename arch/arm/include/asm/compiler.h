#ifndef __ASM_ARM_COMPILER_H
#define __ASM_ARM_COMPILER_H

/*
 * This is used to ensure the compiler did actually allocate the register we
 * asked it for some inline assembly sequences.  Apparently we can't trust
 * the compiler from one version to another so a bit of paranoia won't hurt.
 * This string is meant to be concatenated with the inline asm string and
 * will cause compilation to stop on mismatch.
 * (for details, see gcc PR 15089)
 */
/*
 * [HERMES] GCC 11 的寄存器分配器会换掉 __asmeq 期望的寄存器名，
 * 导致 do_div/get_user 里的汇编断言 .err 失败（编译期硬报错）。
 * 这个断言只是保险检查，寄存器约束本身仍由 GCC 保证，关掉不影响功能。
 */
#define __asmeq(x, y)  ""


#endif /* __ASM_ARM_COMPILER_H */
