import ops
import iopc

TARBALL_FILE="glib-2.54.3.tar.xz"
TARBALL_DIR="glib-2.54.3"
INSTALL_DIR="glib-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
dst_include_dir = ""
dst_lib_dir = ""
src_pkgconfig_dir = ""
dst_pkgconfig_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global dst_include_dir
    global dst_lib_dir
    global src_pkgconfig_dir
    global dst_pkgconfig_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    dst_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_lib_dir = ops.path_join(install_dir, "lib")
    src_pkgconfig_dir = ops.path_join(pkg_path, "pkgconfig")
    dst_pkgconfig_dir = ops.path_join(install_dir, "pkgconfig")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    #ops.exportEnv(ops.addEnv("PATH", ops.path_join(install_tmp_dir, "usr/local/bin")))

    cc_sysroot = ops.getEnv("CC_SYSROOT")

    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')

    ldflags = ""
    ldflags += " -L" + ops.path_join(cc_sysroot, 'lib')
    ldflags += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'usr/lib')

    #ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    #ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    #ops.exportEnv(ops.setEnv("LIBS", libs))
    #extra_conf.append('CFLAGS="-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/libz') + '"')

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    extra_conf = []
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("--disable-libmount")
    extra_conf.append("--disable-fam")
    extra_conf.append("--with-pcre=system")

    cc_sysroot = ops.getEnv("CC_SYSROOT")
    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libz')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libffi')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libpcre3')

    libs = ""
    libs += " -L" + ops.path_join(cc_sysroot, 'lib')
    libs += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    libs += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    libs += " -lz -lffi -lpcre"
                                    
    extra_conf.append('ZLIB_CFLAGS=' + cflags)
    extra_conf.append('ZLIB_LIBS=' + libs)
    extra_conf.append('LIBFFI_CFLAGS=' + cflags)
    extra_conf.append('LIBFFI_LIBS=' + libs)
    extra_conf.append('PCRE_CFLAGS=' + cflags)
    extra_conf.append('PCRE_LIBS=' + libs)
    extra_conf.append("glib_cv_stack_grows=no")
    extra_conf.append("glib_cv_uscore=no")
    extra_conf.append("glib_cv_pcre_has_unicode=yes")

    print extra_conf
    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(dst_lib_dir)

    libgio = "libgio-2.0.so.0.5400.3"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libgio), dst_lib_dir)
    ops.ln(dst_lib_dir, libgio, "libgio-2.0.so.0")
    ops.ln(dst_lib_dir, libgio, "libgio-2.0.so")

    libglib = "libglib-2.0.so.0.5400.3"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libglib), dst_lib_dir)
    ops.ln(dst_lib_dir, libglib, "libglib-2.0.so.0")
    ops.ln(dst_lib_dir, libglib, "libglib-2.0.so")

    libgmodule = "libgmodule-2.0.so.0.5400.3"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libgmodule), dst_lib_dir)
    ops.ln(dst_lib_dir, libgmodule, "libgmodule-2.0.so.0")
    ops.ln(dst_lib_dir, libgmodule, "libgmodule-2.0.so")

    libgobject = "libgobject-2.0.so.0.5400.3"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libgobject), dst_lib_dir)
    ops.ln(dst_lib_dir, libgobject, "libgobject-2.0.so.0")
    ops.ln(dst_lib_dir, libgobject, "libgobject-2.0.so")

    libgthread = "libgthread-2.0.so.0.5400.3"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libgthread), dst_lib_dir)
    ops.ln(dst_lib_dir, libgthread, "libgthread-2.0.so.0")
    ops.ln(dst_lib_dir, libgthread, "libgthread-2.0.so")

    ops.mkdir(dst_include_dir)
    ops.copyto(ops.path_join(tarball_dir, "glib/glibconfig.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), dst_include_dir)

    ops.mkdir(dst_pkgconfig_dir)
    ops.copyto(ops.path_join(src_pkgconfig_dir, '.'), dst_pkgconfig_dir)

    return False

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(dst_lib_dir, "."), "lib")
    iopc.installBin(args["pkg_name"], dst_include_dir, "include")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_pkgconfig_dir, '.'), "pkgconfig")

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

