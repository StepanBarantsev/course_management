from web.app.checks import bp
from flask_login import login_required
from flask import render_template, request, flash, redirect, url_for
from web.app.models import Student, Check
from web.app import db
from flask_login import current_user
from web.app.checks.forms import AddOrEditCheckForm
from web.app.messages import send_message_to_telegram_and_mail
from telegram.chat.messages import get_message_with_course_prefix


@bp.route('/', methods=['GET'])
@login_required
def index():
    student_id = request.args.get('student_id', type=int)
    student = db.session.query(Student).filter(Student.id == student_id).first()
    checks = student.get_all_not_deleted_checks()

    if student.course.author.id == current_user.id:
        return render_template('checks/index.html', title=f"Список чеков студента {student.name}",
                               student_name=student.name, student_id=student.id, course_id=student.course.id,
                               course_name=student.course.name, checks=checks)
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    student_id = request.args.get('student_id', type=int)
    student = db.session.query(Student).filter(Student.id == student_id).first()
    if student.course.author.id == current_user.id:
        checks = student.get_all_not_deleted_checks()
        blocks = student.course.get_all_not_deleted_blocks()
        payed_block_numbers = {check.block.number for check in checks if check.block is not None}
        block_numbers = [str(block.number) for block in blocks if block.number not in payed_block_numbers] + ['Консультация'] + ['Продление']
        form = AddOrEditCheckForm(block_numbers)

        if list(checks) == []:
            is_first_payment = True
        else:
            is_first_payment = False

        if request.method == 'GET':
            form.is_first_payment.data = is_first_payment

        if form.validate_on_submit():
            specific_block_number = form.block_number.data
            link = form.link.data
            amount = form.amount.data
            is_first_payment = form.is_first_payment.data

            if specific_block_number == 'Консультация' or specific_block_number == 'Продление':
                if specific_block_number == "Консультация":
                    text_block = 'консультацию'
                else:
                    text_block = 'продление'
            else:
                text_block = f'блок {specific_block_number}'

            subject = f'{student.course.name}. Оплата за {text_block} получена.'

            if is_first_payment:
                message = get_message_with_course_prefix("FIRST_PAYMENT", student.telegram_id, link, student.course.lms_id,
                                                         current_user.telegram_nickname, student.registration_code, current_user.name)
                # Добавляем два дня бонусом студенту если это первая оплата
                student.number_of_days += 2
            else:
                message = get_message_with_course_prefix("NO_FIRST_PAYMENT", student.telegram_id, text_block, link, current_user.name)

            if specific_block_number == 'Консультация' or specific_block_number == 'Продление':
                new_check = Check(link=link, block_id=None, student_id=student_id, another=specific_block_number, amount=amount)
                if specific_block_number == 'Продление':
                    student.number_of_days += student.course.default_num_days
                    flash(f'Время поддержки студента было увеличено на {student.course.default_num_days} дней!')
            else:
                specific_block = list(filter(lambda block: str(block.number) == specific_block_number, blocks))[0]
                new_check = Check(link=link, block_id=specific_block.id, student_id=student_id, amount=amount)
                student.number_of_days += student.course.default_num_days
                flash(f'Время поддержки студента было увеличено на {student.course.default_num_days} дней!')

            db.session.add(new_check)
            db.session.commit()
            flash('Новый чек был успешно добавлен!')
            if not is_first_payment:
                send_message_to_telegram_and_mail(current_user, student, message, subject,
                                                  render_template('email/payed_block.txt',
                                                                  block_txt=text_block,
                                                                  check_link=link,
                                                                  trainer_name=current_user.name),
                                                  render_template('email/payed_block.html',
                                                                  block_txt=text_block,
                                                                  check_link=link,
                                                                  trainer_name=current_user.name))
            else:
                send_message_to_telegram_and_mail(current_user, student, message, subject,
                                                  render_template('email/payed_first_time.txt',
                                                                  course_id=student.course.lms_id,
                                                                  check_link=link,
                                                                  telegram_nickname=current_user.telegram_nickname,
                                                                  trainer_name=current_user.name,
                                                                  registration_code=student.registration_code),
                                                  render_template('email/payed_first_time.html',
                                                                  course_id=student.course.lms_id,
                                                                  check_link=link,
                                                                  telegram_nickname=current_user.telegram_nickname,
                                                                  trainer_name=current_user.name,
                                                                  registration_code=student.registration_code))
            return redirect(url_for('checks.index', student_id=student_id))

        return render_template('checks/addedit.html', title="Добавление чека студенту",
                               student=student, checks=checks, form=form,
                               flag_emails_from_default_mail=current_user.flag_emails_from_default_mail,
                               add_or_edit="add", telegram_nickname=current_user.telegram_nickname, course_id=student.course.lms_id,
                               trainer_name=current_user.name, registration_code=student.registration_code)
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    student_id = request.args.get('student_id', type=int)
    check_id = request.args.get('check_id', type=int)

    check = db.session.query(Check).filter(Check.id == check_id).first()
    student = db.session.query(Student).filter(Student.id == student_id).first()

    if student.course.author.id == current_user.id:
        checks = student.get_all_not_deleted_checks()
        blocks = student.course.get_all_not_deleted_blocks()
        payed_block_numbers = {check.block.number for check in checks if check.block is not None}
        block_numbers = [str(block.number) for block in blocks if block.number not in payed_block_numbers] + ['Консультация'] + ['Продление']

        if check.block is not None:
            block_numbers.append(str(check.block.number))

        form = AddOrEditCheckForm(block_numbers)

        if form.validate_on_submit():
            specific_block_number = form.block_number.data
            link = form.link.data
            amount = form.amount.data

            check.amount = amount
            check.link = link

            if specific_block_number == 'Консультация' or specific_block_number == 'Продление':
                check.block_id = None
                check.another = specific_block_number
            else:
                specific_block = list(filter(lambda block: str(block.number) == specific_block_number, blocks))[0]
                check.block_id = specific_block.id
                check.another = None

            db.session.commit()
            flash('Чек был успешно отредактирован!')
            return redirect(url_for('checks.index', student_id=student_id))
        elif request.method == 'GET':
            form.amount.data = check.amount
            form.link.data = check.link
            if check.block is not None:
                form.block_number.data = str(check.block.number)
            else:
                form.block_number.data = check.another

        return render_template('checks/addedit.html', title="Редактирование чека студента", student=student,
                               checks=checks, form=form, flag_emails_from_default_mail=True, add_or_edit="edit")
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    student_id = int(request.form['student_id'])
    check_id = int(request.form['check_id'])
    check = db.session.query(Check).filter(Check.id == check_id).first()

    if check.student.course.author.id == current_user.id:
        Check.delete_check_by_id(check_id)
        db.session.commit()
        flash('Чек успешно удален!')
        return redirect(url_for('checks.index', student_id=student_id))
    else:
        return render_template('error/403.html', title='Ошибка доступа')
