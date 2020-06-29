from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'cf88af117254'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('platforms',
                    sa.Column('platform_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('platform_id', name='platforms_pkey'),
                    sa.UniqueConstraint('name', name='platforms_name_key'),
                    postgresql_ignore_search_path=False
                    )

    op.create_table('publishers',
                    sa.Column('publisher_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('publisher_id', name='publishers_pkey'),
                    sa.UniqueConstraint('name', name='publishers_name_key'),
                    postgresql_ignore_search_path=False
                    )

    op.create_table('agreements',
                    sa.Column('agreement_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('title', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('description', sa.VARCHAR(length=64000), autoincrement=False, nullable=True),
                    sa.Column('body', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('valid_from', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('valid_to', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('is_required', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('agreement_id', name='agreements_pkey'),
                    postgresql_ignore_search_path=False
                    )

    op.create_table('release_types',
                    sa.Column('release_type_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('description', sa.VARCHAR(length=2000), autoincrement=False, nullable=False),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('release_type_id', name='release_types_pkey')
                    )

    op.create_table('courses',
                    sa.Column('course_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('platform_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('publisher_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(['platform_id'], ['platforms.platform_id'],
                                            name='courses_platform_id_fkey'),
                    sa.ForeignKeyConstraint(['publisher_id'], ['publishers.publisher_id'],
                                            name='courses_publisher_id_fkey'),
                    sa.PrimaryKeyConstraint('course_id', name='courses_pkey'),
                    postgresql_ignore_search_path=False
                    )

    op.create_table('releases',
                    sa.Column('release_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('description', sa.VARCHAR(length=2000), autoincrement=False, nullable=False),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('course_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('release_type_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], name='releases_course_id_fkey'),
                    sa.ForeignKeyConstraint(['release_type_id'], ['release_types.release_type_id'],
                                            name='releases_release_type_id_fkey'),
                    sa.PrimaryKeyConstraint('release_id', name='releases_pkey')
                    )

    op.create_table('users',
                    sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('email', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('password', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
                    sa.Column('first_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
                    sa.Column('last_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('confirmed', sa.BOOLEAN(), autoincrement=False, nullable=False),
                    sa.Column('confirmed_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('user_id', name='users_pkey'),
                    sa.UniqueConstraint('email', name='users_email_key'),
                    sa.UniqueConstraint('name', name='users_name_key'),
                    postgresql_ignore_search_path=False
                    )

    op.create_table('user_events',
                    sa.Column('user_event_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('log', sa.VARCHAR(length=512), autoincrement=False, nullable=False),
                    sa.Column('meta', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name='user_events_user_id_fkey'),
                    sa.PrimaryKeyConstraint('user_event_id', name='user_events_pkey')
                    )

    op.create_table('user_agreements',
                    sa.Column('user_agreements_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=True),
                    sa.Column('agreements_id', postgresql.UUID(), autoincrement=False, nullable=True),
                    sa.Column('is_read', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('is_accepted', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['agreements_id'], ['agreements.agreement_id'],
                                            name='user_agreements_agreements_id_fkey'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name='user_agreements_user_id_fkey'),
                    sa.PrimaryKeyConstraint('user_agreements_id', name='user_agreements_pkey')
                    )

    op.create_table('keywords',
                    sa.Column('keyword_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('course_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], name='keywords_course_id_fkey'),
                    sa.PrimaryKeyConstraint('keyword_id', name='keywords_pkey')
                    )

    op.create_table('tags',
                    sa.Column('tag_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
                    sa.Column('description', sa.VARCHAR(length=2000), autoincrement=False, nullable=True),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('tag_id', name='tags_pkey'),
                    sa.UniqueConstraint('name', name='tags_name_key'),
                    postgresql_ignore_search_path=False
                    )

    op.create_table('courses_tags',
                    sa.Column('courses_tags_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('tag_id', postgresql.UUID(), autoincrement=False, nullable=True),
                    sa.Column('course_id', postgresql.UUID(), autoincrement=False, nullable=True),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], name='courses_tags_course_id_fkey'),
                    sa.ForeignKeyConstraint(['tag_id'], ['tags.tag_id'], name='courses_tags_tag_id_fkey'),
                    sa.PrimaryKeyConstraint('courses_tags_id', name='courses_tags_pkey')
                    )

    op.create_table('ratings',
                    sa.Column('rating_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('points', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('course_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], name='ratings_course_id_fkey'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name='ratings_user_id_fkey'),
                    sa.PrimaryKeyConstraint('rating_id', name='ratings_pkey')
                    )

    op.create_table('reviews',
                    sa.Column('review_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('description', sa.VARCHAR(length=32768), autoincrement=False, nullable=False),
                    sa.Column('created_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_on', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
                              autoincrement=False, nullable=True),
                    sa.Column('course_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], name='reviews_course_id_fkey'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name='reviews_user_id_fkey'),
                    sa.PrimaryKeyConstraint('review_id', name='reviews_pkey')
                    )


def downgrade():
    op.drop_table('reviews')
    op.drop_table('ratings')
    op.drop_table('courses_tags')
    op.drop_table('tags')
    op.drop_table('keywords')
    op.drop_table('user_agreements')
    op.drop_table('user_events')
    op.drop_table('releases')
    op.drop_table('agreements')
    op.drop_table('release_types')
    op.drop_table('users')
    op.drop_table('courses')
    op.drop_table('platforms')
    op.drop_table('publishers')
