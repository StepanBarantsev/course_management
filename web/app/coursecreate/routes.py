from flask_login import login_required
from web.app.coursecreate import bp
from web.app.models import Course, CourseBlock
from web.app.coursecreate.forms import CreateOrEditCourseForm, CreateOrEditCourseFormAdditional
from flask_login import current_user
from web.app import db
from flask import render_template, redirect, url_for, flash, request, current_app
from sqlalchemy import update


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateOrEditCourseForm(current_user)

    if form.validate_on_submit():

        if not form.is_more_then_one_block.data:
            num_of_blocks = 1
        else:
            if form.number_of_blocks.data is None:
                num_of_blocks = 1
            else:
                num_of_blocks = form.number_of_blocks.data

        new_course = Course(name=form.name.data, user_id=current_user.id, lms_id=form.lms_id.data,
                            trainer_lms_id=form.trainer_lms_id.data,
                            trainer_telegram_id=form.trainer_telegram_id.data,
                            num_of_blocks=num_of_blocks, is_certificate_needed=form.is_certificate_needed.data,
                            default_num_days=form.default_number_of_days.data)

        db.session.add(new_course)
        db.session.commit()
        create_blocks(new_course, num_of_blocks, db)
        flash('Новый курс был успешно создан!')
        return redirect(url_for('main.index'))

    elif request.method == 'GET':
        
        if current_user.telegram_id is not None:
            form.trainer_telegram_id.data = current_user.telegram_id

        if current_user.lms_id is not None:
            form.trainer_lms_id.data = current_user.lms_id

        form.default_number_of_days.data = current_app.config['DEFAULT_NUM_OF_DAYS']

    return render_template('coursecreate/editcreate.html', title='Создать курс', form=form)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    course_id = request.args.get('course_id', 1, type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()

    if course.author.id == current_user.id:
        form = CreateOrEditCourseForm(current_user, course.name, course.lms_id)
        if form.validate_on_submit():

            if not form.is_more_then_one_block.data:
                num_of_blocks = 1
            else:
                if form.number_of_blocks.data is None:
                    num_of_blocks = 1
                else:
                    num_of_blocks = form.number_of_blocks.data

            create_blocks(course, num_of_blocks, db)

            db.session.execute(update(Course).where(Course.id == course_id).values(name=form.name.data, lms_id=form.lms_id.data,
                                                                                   trainer_lms_id=form.trainer_lms_id.data,
                                                                                   trainer_telegram_id=form.trainer_telegram_id.data,
                                                                                   num_of_blocks=num_of_blocks,
                                                                                   is_certificate_needed=form.is_certificate_needed.data,
                                                                                   default_num_days=form.default_number_of_days.data))
            db.session.commit()
            flash('Данные курса были успешно изменены!')
            return redirect(url_for('main.index'))
        elif request.method == 'GET':
            form.name.data = course.name
            form.lms_id.data = course.lms_id
            form.trainer_lms_id.data = course.trainer_lms_id
            form.trainer_telegram_id.data = course.trainer_telegram_id
            form.is_certificate_needed.data = course.is_certificate_needed
            form.default_number_of_days.data = course.default_num_days

            if course.num_of_blocks == 1:
                form.is_more_then_one_block.data = False
            else:
                form.is_more_then_one_block.data = True
                form.number_of_blocks.data = course.num_of_blocks

        return render_template('coursecreate/editcreate.html', title='Редактировать курс', form=form)
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/delete', methods=['POST'])
@login_required
def delete():
    course_id = int(request.form['course_id'])
    course = db.session.query(Course).filter(Course.id == course_id).first()

    if course.author.id == current_user.id:
        Course.delete_course_by_id(course_id)
        db.session.commit()
        flash('Курс успешно удален!')
        return redirect(url_for('main.index'))
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/edit_additional', methods=['GET', 'POST'])
@login_required
def edit_additional():
    course_id = request.args.get('course_id', 1, type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()

    if course.author.id == current_user.id:
        blocks = course.get_all_not_deleted_blocks()
        form = CreateOrEditCourseFormAdditional(blocks=[{"link": block.link, "required_task": block.required_task_lms_id} for block in blocks])
        if form.validate_on_submit():
            for index, block in enumerate(form.blocks):
                database_block = course.get_block_by_num(index + 1)
                database_block.link = block.link.data if block.link.data is not '' else None
                database_block.required_task_lms_id = block.required_task.data if block.required_task.data is not '' else None
                db.session.commit()
            flash('Данные успешно обновлены')
            return redirect(url_for('main.index'))
        elif request.method == 'GET':
            return render_template('coursecreate/edit_additional.html', title='Дополнительные настройки курса', form=form)
    else:
        return render_template('error/403.html', title='Ошибка доступа')


def create_blocks(course, num, db):
    if course.get_all_not_deleted_blocks().count() > num:
        for i in range(course.get_all_not_deleted_blocks().count(), num, -1):
            course.delete_block_by_num(i)
    else:
        for i in range(course.get_all_not_deleted_blocks().count() + 1, num + 1):
            new_block = CourseBlock(number=i, course_id=course.id)
            db.session.add(new_block)

    db.session.commit()



