// 语言包定义
const translations = {
  'zh-CN': {
    // 页面标题
    'page_title': '打卡计时器',
    'page_title_login': '用户登录 - 打卡计时器',
    'page_title_register': '用户注册 - 打卡计时器',
    
    // 登录页
    'login_title': '用户登录',
    'username_label': '用户名',
    'password_label': '密码',
    'login_button': '登录',
    'register_link': '没有账户？立即注册',
    
    // 注册页
    'register_title': '用户注册',
    'register_button': '注册',
    'login_link': '已有账户？立即登录',
    
    // 导航和用户信息
    'user_label': '用户:',
    'logout_link': '退出',
    
    // 主页面内容
    'main_title': '打卡计时器（每日4次）',
    'date_label': '日期',
    'switch_date_btn': '切换日期',
    'punch_now_btn': '记录打卡（当前时间）',
    'manual_time_label': '或手动时间',
    'punch_manual_btn': '按手动时间记录',
    'export_btn': '导出Excel (CSV)',
    
    // 卡片标题
    'today_punches_title': '当日打卡记录',
    'daily_duration_title': '每日打卡时长',
    'second_to_third_timer_title': '第二次到第三次打卡计时',
    'shift_duration_title': '当前班次时长',
    
    // 状态消息
    'no_records': '暂无记录',
    'calculate_after_4_punches': '需满4次打卡后计算',
    'waiting_for_first_punch': '等待第一次打卡',
    'waiting_for_second_punch': '等待第二次打卡',
    'waiting_for_third_punch': '等待第三次打卡',
    'time_since_second_punch': '距离第二次打卡已过:',
    'second_to_third_completed': '第二次到第三次打卡已完成',
    'time_calculation_error': '时间计算错误',
    'second_third_interval': '第二次到第三次间隔: {h}小时{m}分钟',
    'shift_duration': '班次时长: {h}小时{m}分钟{s}秒',
    'waiting_for_punch': '等待打卡开始计时',
    
    // 时间单位
    'hours': '小时',
    'minutes': '分钟',
    'seconds': '秒',
    
    // 提醒模态框
    'reminder_title': '⏰ 打卡提醒',
    'reminder_message': '您已打开应用超过4小时55分钟，记得及时打卡哦！',
    'punch_now_reminder_btn': '立即打卡',
    'later_reminder_btn': '稍后提醒',
    
    // 打卡报告
    'punch_number': '第{n}次',
    'interval': '间隔',
    'daily_total': '每日打卡时长',
    'time': '时间',
    'actions': '操作',
    'delete': '删除',
    
    // 对话框和确认消息
    'confirm_delete': '确定要删除这条打卡记录吗？',
    'delete_failed': '删除失败',
    
    // 错误消息
    'no_record_today': '该日期暂无打卡记录',
    'insufficient_punches': '记录不足4次，缺少 {n} 次',
    'time_order_error': '时间顺序异常，请检查打卡',
    'punch_full': '当日已满4次打卡',
    
    // 成功消息
    'punch_recorded': '已记录第 {n} 次打卡',
    'export_success': '已导出 CSV，可用 Excel 打开',
    'delete_success': '删除成功',
    
    // 导出表头
    'export_date': '日期',
    'export_count': '记录数',
    'export_punch1': '第1次',
    'export_punch2': '第2次',
    'export_punch3': '第3次',
    'export_punch4': '第4次',
    'export_interval1': '间隔(1-2)',
    'export_interval2': '间隔(3-4)',
    'export_total': '总时长',
    'export_status': '状态',
    
    // 其他
    'date_switched': '已切换日期',
    'export_failed': '导出失败',
    'enter_manual_time': '请输入手动时间',
    
    // 末班打卡
    'late_shift_checkbox': '末班打卡',
    'late_shift_punch': '末班打卡',
    'dual_record': '双记录',
  },
  
  'en': {
    // Page titles
    'page_title': 'Punch Timer',
    'page_title_login': 'User Login - Punch Timer',
    'page_title_register': 'User Registration - Punch Timer',
    
    // Login page
    'login_title': 'User Login',
    'username_label': 'Username',
    'password_label': 'Password',
    'login_button': 'Login',
    'register_link': 'No account? Register now',
    
    // Register page
    'register_title': 'User Registration',
    'register_button': 'Register',
    'login_link': 'Already have an account? Login now',
    
    // Navigation and user info
    'user_label': 'User:',
    'logout_link': 'Logout',
    
    // Main page content
    'main_title': 'Punch Timer (4 Times Daily)',
    'date_label': 'Date',
    'switch_date_btn': 'Switch Date',
    'punch_now_btn': 'Punch In (Current Time)',
    'manual_time_label': 'Or Manual Time',
    'punch_manual_btn': 'Punch In by Manual Time',
    'export_btn': 'Export to Excel (CSV)',
    
    // Card titles
    'today_punches_title': 'Today\'s Punch Records',
    'daily_duration_title': 'Daily Punch Duration',
    'second_to_third_timer_title': 'Second to Third Punch Timer',
    'shift_duration_title': 'Current Shift Duration',
    
    // Status messages
    'no_records': 'No records',
    'calculate_after_4_punches': 'Calculation available after 4 punches',
    'waiting_for_first_punch': 'Waiting for first punch',
    'waiting_for_second_punch': 'Waiting for second punch',
    'waiting_for_third_punch': 'Waiting for third punch',
    'time_since_second_punch': 'Time since second punch:',
    'second_to_third_completed': 'Second to third punch completed',
    'time_calculation_error': 'Time calculation error',
    'second_third_interval': 'Second to third interval: {h}h {m}m',
    'shift_duration': 'Shift duration: {h}h {m}m {s}s',
    'waiting_for_punch': 'Waiting for punch to start timing',
    
    // Time units
    'hours': ' hours',
    'minutes': ' minutes',
    'seconds': ' seconds',
    
    // Reminder modal
    'reminder_title': '⏰ Punch Reminder',
    'reminder_message': 'You have been using the app for over 4 hours and 55 minutes. Remember to punch in!',
    'punch_now_reminder_btn': 'Punch In Now',
    'later_reminder_btn': 'Remind Me Later',
    
    // Punch report
    'punch_number': 'Punch #{n}',
    'interval': 'Interval',
    'daily_total': 'Daily Total',
    'time': 'Time',
    'actions': 'Actions',
    'delete': 'Delete',
    
    // Dialogs and confirmation messages
    'confirm_delete': 'Are you sure you want to delete this punch record?',
    'delete_failed': 'Failed to delete',
    
    // Error messages
    'no_record_today': 'No punch records for this date',
    'insufficient_punches': 'Insufficient punches, missing {n} punches',
    'time_order_error': 'Time order error, please check your punches',
    'punch_full': 'Already reached 4 punches for today',
    
    // Success messages
    'punch_recorded': 'Punch #{n} recorded',
    'export_success': 'CSV exported, can be opened in Excel',
    'delete_success': 'Successfully deleted',
    
    // Export headers
    'export_date': 'Date',
    'export_count': 'Count',
    'export_punch1': 'Punch 1',
    'export_punch2': 'Punch 2',
    'export_punch3': 'Punch 3',
    'export_punch4': 'Punch 4',
    'export_interval1': 'Interval (1-2)',
    'export_interval2': 'Interval (3-4)',
    'export_total': 'Total',
    'export_status': 'Status',
    
    // Others
    'date_switched': 'Date switched',
    'export_failed': 'Export failed',
    'enter_manual_time': 'Please enter manual time',
    
    // Late shift punch
    'late_shift_checkbox': 'Late Shift',
    'late_shift_punch': 'Late Shift Punch',
    'dual_record': 'Dual Record',
  },
  
  'es': {
    // Títulos de página
    'page_title': 'Temporizador de Registro',
    'page_title_login': 'Inicio de Sesión - Temporizador de Registro',
    'page_title_register': 'Registro de Usuario - Temporizador de Registro',
    
    // Página de inicio de sesión
    'login_title': 'Inicio de Sesión',
    'username_label': 'Nombre de Usuario',
    'password_label': 'Contraseña',
    'login_button': 'Iniciar Sesión',
    'register_link': '¿No tienes cuenta? Regístrate ahora',
    
    // Página de registro
    'register_title': 'Registro de Usuario',
    'register_button': 'Registrarse',
    'login_link': '¿Ya tienes una cuenta? Inicia sesión ahora',
    
    // Navegación e información de usuario
    'user_label': 'Usuario:',
    'logout_link': 'Cerrar Sesión',
    
    // Contenido principal
    'main_title': 'Temporizador de Registro (4 Veces al Día)',
    'date_label': 'Fecha',
    'switch_date_btn': 'Cambiar Fecha',
    'punch_now_btn': 'Registrar (Hora Actual)',
    'manual_time_label': 'O Hora Manual',
    'punch_manual_btn': 'Registrar por Hora Manual',
    'export_btn': 'Exportar a Excel (CSV)',
    
    // Títulos de tarjetas
    'today_punches_title': 'Registros de Hoy',
    'daily_duration_title': 'Duración Diaria de Registros',
    'second_to_third_timer_title': 'Temporizador de Segundo a Tercer Registro',
    'shift_duration_title': 'Duración del Turno Actual',
    
    // Mensajes de estado
    'no_records': 'Sin registros',
    'calculate_after_4_punches': 'Cálculo disponible después de 4 registros',
    'waiting_for_first_punch': 'Esperando primer registro',
    'waiting_for_second_punch': 'Esperando segundo registro',
    'waiting_for_third_punch': 'Esperando tercer registro',
    'time_since_second_punch': 'Tiempo desde el segundo registro:',
    'second_to_third_completed': 'Segundo a tercer registro completado',
    'time_calculation_error': 'Error en el cálculo del tiempo',
    'second_third_interval': 'Intervalo de segundo a tercero: {h}h {m}m',
    'shift_duration': 'Duración del turno: {h}h {m}m {s}s',
    'waiting_for_punch': 'Esperando registro para iniciar el temporizador',
    
    // Unidades de tiempo
    'hours': ' horas',
    'minutes': ' minutos',
    'seconds': ' segundos',
    
    // Modal de recordatorio
    'reminder_title': '⏰ Recordatorio de Registro',
    'reminder_message': 'Ha estado usando la aplicación por más de 4 horas y 55 minutos. ¡Recuerde registrar su tiempo!',
    'punch_now_reminder_btn': 'Registrar Ahora',
    'later_reminder_btn': 'Recordarme Más Tarde',
    
    // Reporte de registros
    'punch_number': 'Registro #{n}',
    'interval': 'Intervalo',
    'daily_total': 'Total Diario',
    'time': 'Hora',
    'actions': 'Acciones',
    'delete': 'Eliminar',
    
    // Diálogos y mensajes de confirmación
    'confirm_delete': '¿Está seguro de que desea eliminar este registro?',
    'delete_failed': 'Error al eliminar',
    
    // Mensajes de error
    'no_record_today': 'No hay registros para esta fecha',
    'insufficient_punches': 'Registros insuficientes, faltan {n} registros',
    'time_order_error': 'Error en el orden de tiempo, por favor revise sus registros',
    'punch_full': 'Ya se alcanzaron los 4 registros para hoy',
    
    // Mensajes de éxito
    'punch_recorded': 'Registro #{n} guardado',
    'export_success': 'CSV exportado, puede abrirse en Excel',
    'delete_success': 'Eliminado correctamente',
    
    // Encabezados de exportación
    'export_date': 'Fecha',
    'export_count': 'Cantidad',
    'export_punch1': 'Registro 1',
    'export_punch2': 'Registro 2',
    'export_punch3': 'Registro 3',
    'export_punch4': 'Registro 4',
    'export_interval1': 'Intervalo (1-2)',
    'export_interval2': 'Intervalo (3-4)',
    'export_total': 'Total',
    'export_status': 'Estado',
    
    // Otros
    'date_switched': 'Fecha cambiada',
    'export_failed': 'Error al exportar',
    'enter_manual_time': 'Por favor ingrese la hora manual',
    
    // Registro de turno nocturno
    'late_shift_checkbox': 'Turno Nocturno',
    'late_shift_punch': 'Registro de Turno Nocturno',
    'dual_record': 'Registro Doble',
  }
};

// 获取翻译文本
function getTranslation(key, lang = getCurrentLanguage()) {
  // 如果当前语言包中没有该键，则回退到中文
  if (!translations[lang] || !translations[lang][key]) {
    // 如果中文包中也没有该键，则返回键名本身
    if (!translations['zh-CN'] || !translations['zh-CN'][key]) {
      return key;
    }
    return translations['zh-CN'][key];
  }
  return translations[lang][key];
}

// 获取当前语言
function getCurrentLanguage() {
  // 首先检查localStorage中是否有保存的语言设置
  const savedLang = localStorage.getItem('language');
  if (savedLang && translations[savedLang]) {
    return savedLang;
  }
  
  // 否则根据浏览器语言设置判断
  const browserLang = navigator.language || navigator.userLanguage;
  if (browserLang.startsWith('en')) {
    return 'en';
  } else if (browserLang.startsWith('es')) {
    return 'es';
  } else {
    return 'zh-CN'; // 默认中文
  }
}

// 设置当前语言
function setCurrentLanguage(lang) {
  if (translations[lang]) {
    // 保存到localStorage
    localStorage.setItem('language', lang);
    // 更新HTML的lang属性
    document.documentElement.lang = lang;
    return true;
  }
  return false;
}

// 翻译带有参数的文本
function translateWithParams(key, params, lang = getCurrentLanguage()) {
  let translation = getTranslation(key, lang);
  
  // 替换参数 {n} -> 实际值
  for (const param in params) {
    translation = translation.replace(`{${param}}`, params[param]);
  }
  
  return translation;
}
