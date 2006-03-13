dnl Copyright (C) 2003  CEA/DEN, EDF R&D

AC_DEFUN([CHECK_HTML_GENERATORS],[

#AC_CHECKING(for html generators)

doxygen_ok=yes
dnl were is doxygen ?
AC_PATH_PROG(DOXYGEN,doxygen) 
if test "x$DOXYGEN" = "x"
then
  AC_MSG_WARN(doxygen not found)
  doxygen_ok=no
fi
dnl AC_SUBST(DOXYGEN)

graphviz_ok=yes
dnl were is graphviz ?
AC_PATH_PROG(DOT,dot) 
if test "x$DOT" = "x" ; then
  AC_MSG_WARN(graphviz not found)
  graphviz_ok=no
fi
dnl AC_SUBST(DOT)

AC_PATH_PROG(LATEX,latex) 
if test "x$LATEX" = "x" ; then
  AC_MSG_WARN(latex not found)
fi
AC_SUBST(LATEX)

AC_PATH_PROG(DVIPS,dvips)
if test "x$DVIPS" = "x" ; then
  AC_MSG_WARN(dvips not found)
fi
AC_SUBST(DVIPS)

AC_PATH_PROG(PDFLATEX,pdflatex)
if test "x$PDFLATEX" = "x" ; then
  AC_MSG_WARN(pdflatex not found)
fi
AC_SUBST(PDFLATEX)

rst2html_ok=yes
dnl were is rst2html ?
AC_PATH_PROG(RST2HTML,rst2html) 
if test "x$RST2HTML" = "x"; then
  AC_PATH_PROG(RST2HTML,rst2html.py)
fi

if test "x$RST2HTML" = "x"; then
  AC_MSG_WARN(rst2html not found)
  rst2html_ok=no
fi
AC_SUBST(RST2HTML)

AM_CONDITIONAL(RST2HTML_IS_OK, [test x"$rst2html_ok" = xyes])

])dnl
dnl
